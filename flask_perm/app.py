# -*- coding: utf-8 -*-

import logging
from functools import wraps
from flask import session, request
from sqlalchemy.exc import IntegrityError
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
        self._admin_logger = logging.getLogger('flask_perm.admin')
        self.registered_permissions = set()
        if app is not None:
            self.init_app(app)

    @property
    def admin_logger(self):
        return self._admin_logger

    @admin_logger.setter
    def admin_logger(self, logger):
        self._admin_logger = logger

    def init_app(self, app):
        """Initialize Perm object.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['perm'] = self

        db.app = app
        db.init_app(app)

        bcrypt.app = app
        bcrypt.init_app(app)

        app.config.setdefault('PERM_ADMIN_PREFIX', '/perm-admin')
        app.config.setdefault('PERM_ADMIN_ECHO', False)

        from . import models
        db.create_all()

        from .api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix=app.config.get('PERM_ADMIN_PREFIX') + '/api')

        from .admin import bp as admin_bp
        app.register_blueprint(admin_bp, url_prefix=app.config.get('PERM_ADMIN_PREFIX'))

        self.register_context_processors(app)



    def log_admin_action(self, msg):
        '''Log msg to `flask.admin` logger.'''
        if self.app.config.get('PERM_ADMIN_ECHO'):
            self.admin_logger.info(msg)

    def require_perm_admin(self, f):
        '''A decorator that can protect function from unauthorized request.

        Used in perm admin dashboard.'''
        @wraps(f)
        def _(*args, **kwargs):
            if not session.get('perm_admin_id'):
                raise self.Denied
            return f(*args, **kwargs)
        return _

    def create_super_admin(self, email, password):
        """Create superadmin / Reset password."""
        from .services import SuperAdminService
        try:
            superadmin = SuperAdminService.create(email, password)
        except IntegrityError:
            superadmin = SuperAdminService.get_by_email(email)
            superadmin = SuperAdminService.reset_password(superadmin.id, password)
        return SuperAdminService.to_dict(superadmin)

    def login_perm_admin(self, super_admin_id):
        """Get authorization to access perm admin dashboard."""
        session['perm_admin_id'] = super_admin_id

    def logout_perm_admin(self):
        """Revoke authorization from accessing perm admin dashboard."""
        session.pop('perm_admin_id', None)

    def get_perm_admin_id_from_session(self):
        from .services import SuperAdminService
        admin_id = session.get('perm_admin_id')
        super_admin = admin_id and SuperAdminService.get(admin_id)
        return super_admin and super_admin.id

    def get_perm_admin_id_by_auth(self, email, password):
        from .services import SuperAdminService
        if SuperAdminService.verify_password(email, password):
            super_admin = SuperAdminService.get_by_email(email)
            return super_admin and super_admin.id

    def get_perm_admin_id(self):
        """Get super admin id. Both basic authorization and cookie are support."""
        if request.authorization:
            auth = request.authorization
            return self.get_perm_admin_id_by_auth(auth.username, auth.password)
        return self.get_perm_admin_id_from_session()

    def has_perm_admin_logined(self):
        """"""
        return bool(self.get_perm_admin_id())

    def user_loader(self, callback):
        """Define user loader.

        Required if you plan to use perm admin dashboard.
        The callback will be used to render user basic information in dashboard.

        Callback must take `user_id` integer parameter.
        """
        self.user_callback = callback
        return callback

    def current_user_loader(self, callback):
        """Define current user loader.

        Required if you plan to use decorator to protect your function.
        The callback will be used in deciding whether current user has authority.

        Callback takes no parameters.
        """
        self.current_user_callback = callback
        return callback

    def users_loader(self, callback):
        """Define users loader.

        Required if you plan to use perm admin dashboard.
        The callback will be used to render whole user list in dashboard.

        Callback must take 5 parameters:
        * filter_by={},
        * sort_field='created_at',
        * sort_dir='desc',
        * offset=0,
        * limit=20
        """
        self.users_callback = callback
        return callback

    def users_count_loader(self, callback):
        """Define users count loader.

        Required if you plan to use perm admin dashboard.
        The callback will be used in paginating user list.

        Callback takes no parameters."""
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
        """Decide whether a user has a permission identified by `codes`.

        Code is defined in perm admin dashboard."""

        from .services import VerificationService, PermissionService

        permission = PermissionService.get_by_code(code)

        if not permission:
            return False

        return VerificationService.has_permission(user_id, permission.id)

    def has_permissions(self, user_id, *codes):
        """Decide whether a user has permissions identified by `codes`.

        Codes are defined in perm admin dashboard."""
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
        """Define all permission codes that authorized to a user.

        Codes are defined in perm admin dashboard."""
        from .services import VerificationService, PermissionService

        permission_ids = VerificationService.get_user_permissions(user_id)

        permissions = map(PermissionService.get, permission_ids)
        permissions = filter(None, permissions)
        permissions = map(PermissionService.rest, permissions)

        return permissions

    def get_all_permission_codes(self):
        """Get all permission codes.

        WARNING: this might have performance issue."""

        from .services import PermissionService

        permissions = PermissionService.get_permissions()

        return [permission.code for permission in permissions]

    def is_user_in_groups(self, user_id, *groups):
        """Decide whether a user is in groups.

        Groups are defined in perm admin dashboard."""
        from .services import UserGroupService, UserGroupMemberService

        if not groups:
            return False

        if '*' in groups:
            user_group_ids = UserGroupService.get_all_user_group_ids()
        else:
            user_groups = UserGroupService.get_user_groups_by_codes(groups)
            user_group_ids = [user_group.id for user_group in user_groups]

        if not user_group_ids:
            return False

        return UserGroupMemberService.is_user_in_groups(user_id, user_group_ids)

    def require_group(self, *groups):
        """A decorator that can decide whether current user is in listed groups.

        Groups are defined in perm admin dashboard."""
        from .services import UserGroupService, UserGroupMemberService


        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):

                current_user = self.load_current_user()

                if not current_user:
                    raise self.Denied

                current_user_id = current_user.id
                is_allowed = self.is_user_in_groups(current_user_id, *groups)

                if is_allowed:
                    return func(*args, **kwargs)
                else:
                    raise self.Denied
            return _
        return deco

    def require_group_in_template(self, *groups):
        """Require group in template"""
        from .services import UserGroupService, UserGroupMemberService

        current_user = self.load_current_user()

        if not current_user:
            return False

        current_user_id = current_user.id
        return self.is_user_in_groups(current_user_id, *groups)


    def require_permission(self, *codes):
        """A decorator that can decide whether current user has listed permission codes.

        Codes are defined in perm admin dashboard."""

        for code in codes:
            self.registered_permissions.add(code)

        def deco(func):
            @wraps(func)
            def _(*args, **kwargs):
                current_user = self.load_current_user()

                if not current_user:
                    raise self.Denied

                is_allowed = self.has_permissions(current_user.id, *codes)

                if is_allowed:
                    return func(*args, **kwargs)
                else:
                    raise self.Denied

            return _
        return deco

    def require_permission_in_template(self, *codes):
        """Require permission in template."""
        for code in codes:
            self.registered_permissions.add(code)

        current_user = self.load_current_user()

        if not current_user:
            return False

        return self.has_permissions(current_user.id, *codes)

    def default_context_processors(self):
        return {
            'require_permission': self.require_permission_in_template,
            'require_group': self.require_group_in_template,
        }

    def register_commands(self, flask_script_manager):
        """Register several convinient Flask-Script commands.

        WARNING: make sure you have installed Flask-Script.

        :param flask_script_manager: a flask.ext.script.Manager object.
        """
        from .script import perm_manager
        flask_script_manager.add_command('perm', perm_manager)

    def register_context_processors(self, app):
        """Register default context processors to app.
        """
        app.context_processor(self.default_context_processors)
