# -*- coding: utf-8 -*-

import logging
from functools import wraps
from flask import session, request
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from .core import db, bcrypt

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
        self.registered_permissions = set()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configuration Items:

        * PERM_DB
        * PERM_USERS_GETTER
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['perm'] = self

        db.app = app
        db.init_app(app)

        bcrypt.app = app
        bcrypt.init_app(app)

        app.config.setdefault('PERM_ADMIN_API_PREFIX', '/perm-admin/api')
        app.config.setdefault('PERM_ADMIN_PREFIX', '/perm-admin')
        app.config.setdefault('PERM_ADMIN_ECHO', False)

        if app.config.get('PERM_ADMIN_ECHO'):
            self.admin_logger.setLevel(logging.INFO)
            self.admin_logger.addHandler(logging.StreamHandler())

        from . import models
        db.create_all()

        from .controllers import bp as api_bp
        api_bp.perm = self
        app.register_blueprint(api_bp, url_prefix=app.config.get('PERM_ADMIN_API_PREFIX'))

        from .admin import bp as admin_bp
        admin_bp.perm = self
        app.register_blueprint(admin_bp, url_prefix=app.config.get('PERM_ADMIN_PREFIX'))

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

    def login_perm_admin(self, super_admin_id):
        session['perm_admin_id'] = super_admin_id

    def logout_perm_admin(self):
        session.pop('perm_admin_id', None)

    def get_perm_admin_id_from_session(self):
        return session.get('perm_admin_id')

    def get_perm_admin_id_by_auth(self, email, password):
        from .services import SuperAdminService
        if SuperAdminService.verify_password(email, password):
            super_admin = SuperAdminService.get_by_email(email)
            return super_admin and super_admin.id

    def get_perm_admin_id(self):
        if request.authorization:
            auth = request.authorization
            return self.get_perm_admin_id_by_auth(auth.username, auth.password)
        return self.get_perm_admin_id_from_session()

    def has_perm_admin_logined(self):
        return bool(self.get_perm_admin_id())

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

    def load_users(self, filter_by={}, sort_field='created_at', sort_dir='desc', offset=0, limit=20):
        if self.users_callback is None:
            raise NotImplementedError('You must register users_loader!')
        return self.users_callback(**dict(
            filter_by=filter_by,
            sort_field=sort_field,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        ))

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

    def has_permissions(self, user_id, *codes):
        if not codes:
            return True
        if '*' in codes:
            return any(
                self.has_permission(user_id, code)
                for code in self.get_all_permission_codes()
            )
        else:
            return any(self.has_permission(user_id, code) for code in codes)

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

    def require_group(self, *groups):
        from .services import UserGroupService, UserGroupMemberService

        if self.current_user_callback is None:
            raise NotImplementedError('You must register current_user_loader!')

        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):
                current_user = self.current_user_callback()

                if not current_user:
                    raise self.Denied

                current_user_id = current_user.id

                if not groups:
                    is_allowed = True
                elif '*' in groups:
                    is_allowed = True
                else:
                    user_groups = UserGroupService.get_user_groups_by_codes(groups)
                    user_group_ids = [user_group.id for user_group in user_groups]
                    if not user_group_ids:
                        is_allowed = False
                    else:
                        is_allowed = UserGroupMemberService.is_user_in_groups(
                            current_user_id, user_group_ids)
                if is_allowed:
                    return func(*args, **kwargs)
                else:
                    raise self.Denied
            return _
        return deco

    def require_permission(self, *codes):
        if self.current_user_callback is None:
            raise NotImplementedError('You must register current_user_loader!')

        for code in codes:
            self.registered_permissions.add(code)

        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):

                current_user = self.current_user_callback()
                if not current_user:
                    raise self.Denied

                is_allowed = self.has_permissions(current_user.id, *codes)

                if is_allowed:
                    return func(*args, **kwargs)
                else:
                    raise self.Denied

            return _
        return deco
