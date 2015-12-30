# -*- coding: utf-8 -*-

from functools import wraps

from .core import db

class Perm(object):

    class Denied(Exception):
        pass

    def __init__(self, app=None):
        self.app = app
        self.user_callback = None
        self.current_user_callback = None
        self.users_callback = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configuration Items:

        * PERM_DB
        * PERM_USERS_GETTER
        """
        db.app = app
        db.init_app(app)

        app.config.setdefault('PERM_USERS_GETTER', lambda: [])
        app.config.setdefault('PERM_URL_PERFIX', '/perm')
        app.config.setdefault('PERM_CURRENT_USER_ACCESS_VALIDATOR', lambda user: False)

        from . import models
        db.create_all()

        from .controllers import bp
        bp.perm = self
        app.register_blueprint(bp, url_prefix=app.config.get('PERM_URL_PREFIX'))

    def user_loader(self, callback):
        self.user_callback = callback
        return callback

    def current_user_loader(self, callback):
        self.current_user_callback = callback
        return callback

    def users_loader(self, callback):
        self.users_callback = callback
        return callback

    def load_user(self, user_id):
        if self.user_callback is None:
            raise NotImplementedError('You must register user_loader!')
        return self.user_callback(user_id)

    def load_current_user(self):
        if self.current_user_callback is None:
            raise NotImplementedError('You must register current_user_loader!')
        return self.current_user_callback()

    def load_users(self):
        if self.users_callback is None:
            raise NotImplementedError('You must register users_loader!')
        return self.users_callback()

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

    def get_all_permission_codes(self):
        from .services import PermissionService
        permissions = PermissionService.get_permissions()
        return [permission.code for permission in permissions]

    def require_permission(self, *codes):
        if self.current_user_callback is None:
            raise NotImplementedError('You must register current_user_loader!')

        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):

                current_user = self.current_user_callback()
                current_user_id = current_user.id

                if not codes:
                    is_allowed = True
                if '*' in codes:
                    is_allowed = any(
                        self.has_permission(current_user_id, code)
                        for code in self.get_all_permission_codes()
                    )
                else:
                    is_allowed = any(self.has_permission(current_user_id, code) for code in codes)

                if is_allowed:
                    return func(*args, **kwargs)
                else:
                    raise self.__class__.Denied

            return _
        return deco
