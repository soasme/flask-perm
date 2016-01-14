# -*- coding: utf-8 -*-

from functools import wraps
from flask import session
from .core import db

class Perm(object):

    class Denied(Exception):
        pass

    def __init__(self, app=None):
        self.app = app
        self.user_callback = None
        self.current_user_callback = None
        self.users_callback = None
        self.users_count_callback = None
        self.admin_logger = logging.getLogger('flask_perm.admin')
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
        app.config.setdefault('PERM_CURRENT_USER_ACCESS_VALIDATOR', lambda user: False)
        app.config.setdefault('PERM_ADMIN_API_PREFIX', '/perm-admin/api')
        app.config.setdefault('PERM_ADMIN_PREFIX', '/perm-admin')

        if app.config.get('PERM_ADMIN_ECHO'):
            self.admin_logger.setLevel(logging.INFO)
            self.admin_logger.addHandler(logging.StreamHandler())

        from . import models
        db.create_all()

        from .controllers import bp as api_bp
        api_bp.perm = self
        app.register_blueprint(api_bp, url_prefix=app.config.get('PERM_ADMIN_API_PREFIX'))
    def log_admin_action(self, msg):
        if self.app.config.get('PERM_ADMIN_ECHO'):
            self.admin_logger.info(msg)

    def require_perm_admin(self, f):
        @wraps(f)
        def _(*args, **kwargs):
            if not session.get('perm_admin'):
                raise self.Denied
            return f(*args, **kwargs)
        return _

    def login_perm_admin(self):
        session['perm_admin'] = '1'

    def logout_perm_admin(self):
        session.pop('perm_admin', None)

    def has_perm_admin_logined(self):
        return session.get('perm_admin') == '1'

    def check_perm_admin_auth(self, username, password):
        return username == self.app.config.get('PERM_ADMIN_USERNAME') and \
            password == self.app.config.get('PERM_ADMIN_PASSWORD')

    def user_loader(self, callback):
        self.user_callback = callback
        return callback

    def current_user_loader(self, callback):
        self.current_user_callback = callback
        return callback

    def users_loader(self, callback):
        self.users_callback = callback
        return callback

    def users_count_loader(self, callback):
        self.users_count_callback = callback
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
    def load_users_count(self):
        if self.users_count_callback is None:
            raise NotImplementedError('You must register users_count_loader')
        return self.users_count_callback()

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
