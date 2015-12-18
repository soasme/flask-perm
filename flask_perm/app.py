# -*- coding: utf-8 -*-

from functools import wraps

from flask import _app_ctx_stack as stack

from .core import init_db

class Perm(object):

    class Denied(Exception):
        pass

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configuration Items:

        * PERM_DB
        * PERM_USER_GETTER
        * PERM_USERS_GETTER
        * PERM_CURRENT_USER_GETTER
        """
        init_db(app.config.get('PERM_DB'))

        app.config.setdefault('PERM_USER_GETTER', lambda id: None)
        app.config.setdefault('PERM_USERS_GETTER', lambda: [])
        app.config.setdefault('PERM_CURRENT_USER_GETTER', lambda: None)
        app.config.setdefault('PERM_URL_PERFIX', '/perm')

        from .controllers import bp
        app.register_blueprint(bp, url_prefix=app.config.get('PERM_URL_PREFIX'))

    def has_permission(self, user_id, code):
        from .services import VerificationService, PermissionService
        permission = PermissionService.get_by_code(code)
        if not permission:
            return False
        return VerificationService.has_permission(user_id, permission.id)

    def get_user_permissions(self, user_id):
        from .services import VerificationService, PermissionService
        permission_ids = VerificationService.get_user_permissions(user_id)
        permissions = map(PermissionService.get, permission_ids)
        permissions = filter(None, permissions)
        permissions = map(PermissionService.rest, permissions)
        return permissions

    def require_permission(self, *codes):
        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):
                current_user = self.app.config['PERM_CURRENT_USER_GETTER']()
                current_user_id = current_user['id']
                if not codes:
                    return func(*args, **kwargs)
                if any(self.has_permission(current_user_id, code) for code in codes):
                    return func(*args, **kwargs)
                raise self.__class__.Denied
            return _
        return deco
