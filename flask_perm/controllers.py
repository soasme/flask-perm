# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from .services import (
    UserGroupService, PermissionService, UserGroupMemberService,
    UserPermissionService, UserGroupPermissionService,
    VerificationService,
)

bp = Blueprint('flask_perm_api', __name__)

def ok(**data):
    return jsonify(code=0, message='success', data=data)

def bad_request(message='bad request', **data):
    return jsonify(code=1, message=message, data=data), 400

def not_found(message='not found', **data):
    return jsonify(code=1, message=message, data=data), 404

@bp.before_request
def before_request():
    if not current_app.config['PERM_CURRENT_USER_ACCESS_VALIDATOR']():
        return jsonify(code=1, message='forbidden', data={}), 403

@bp.route('/permissions', methods=['POST'])
def add_permission():
    data = request.get_json()
    if 'title' not in data:
        return bad_request('missing title field')
    if not data['title']:
        return bad_request('title is blank')
    title = data['title']
    code = data.get('code')
    permission = PermissionService.create(title, code)
    permission = PermissionService.rest(permission)
    return ok(permission=permission)

@bp.route('/permissions')
def get_permissions():
    permissions = PermissionService.get_permissions()
    permissions = map(PermissionService.rest, permissions)
    return ok(permissions=permissions)

@bp.route('/permissions/<int:permission_id>')
def get_permission(permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    permission = PermissionService.rest(permission)
    return ok(permission=permission)

@bp.route('/permissions/<int:permission_id>', methods=['PATCH'])
def update_permission(permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    if request.get_json().get('title'):
        PermissionService.rename(permission_id, request.get_json().get('title'))
    if request.get_json().get('code'):
        PermissionService.set_code(permission_id, request.get_json().get('code'))
    permission = PermissionService.rest(PermissionService.get(permission_id))
    return ok(permission=permission)

@bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
def delete_permission(permission_id):
    # TODO: delete user_permission, user_group_permission by permission
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    PermissionService.delete(permission_id)
    return ok()

@bp.route('/permissions/<int:permission_id>/users/<int:user_id>', methods=['PUT'])
def add_user_permission(user_id, permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    UserPermissionService.create(user_id, permission_id)
    return ok()

@bp.route('/permissions/<int:permission_id>/users/<int:user_id>', methods=['DELETE'])
def revoke_user_permission(user_id, permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    UserPermissionService.delete(user_id, permission_id)
    return ok()

@bp.route('/permissions/<int:permission_id>/user_groups/<int:user_group_id>', methods=['PUT'])
def add_user_group_permission(user_group_id, permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    UserGroupPermissionService.create(user_group_id, permission_id)
    return ok()

@bp.route('/permissions/<int:permission_id>/user_groups/<int:user_group_id>', methods=['DELETE'])
def revoke_user_group_permission(user_group_id, permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    UserGroupPermissionService.delete(user_group_id, permission_id)
    return ok()

@bp.route('/users/<int:user_id>/permissions')
def get_user_permissions(user_id):
    only = request.args.get('only')
    if only == 'user':
        permission_ids = set(UserPermissionService.get_permissions_by_user(user_id))
    elif only == 'user_group':
        permission_ids = VerificationService.get_user_group_permissions_by_user(user_id)
    else:
        permission_ids = VerificationService.get_user_permissions(user_id)
    permissions = map(PermissionService.get, permission_ids)
    permissions = map(PermissionService.rest, permissions)
    return ok(permissions=permissions)

@bp.route('/user_groups', methods=['POST'])
def add_user_group():
    data = request.get_json()
    if 'title' not in data:
        return bad_request('missing title field')
    if not data['title']:
        return bad_request('title is blank')
    user_group = UserGroupService.create(data['title'])
    user_group = UserGroupService.rest(user_group)
    return ok(user_group=user_group)

@bp.route('/user_groups')
def get_user_groups():
    user_groups = UserGroupService.get_user_groups()
    user_groups = map(UserGroupService.rest, user_groups)
    return ok(user_groups=user_groups)

@bp.route('/user_groups/<int:user_group_id>', methods=['PATCH'])
def update_user_group(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    data = request.get_json()
    if 'title' in data and data['title']:
        UserGroupService.rename(user_group_id, data['title'])
    user_group = UserGroupService.rest(UserGroupService.get(user_group_id))
    return ok(user_group=user_group)

@bp.route('/user_groups/<int:user_group_id>', methods=['DELETE'])
def delete_user_group(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    UserGroupService.delete(user_group_id)
    return ok()

@bp.route('/user_groups/<int:user_group_id>/users')
def get_user_group_members(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    user_ids = UserGroupMemberService.get_users_by_group(user_group_id)
    users = map(current_app.config['PERM_USER_GETTER'], user_ids)
    return ok(users=users)

@bp.route('/user_groups/<int:user_group_id>/users/<int:user_id>', methods=['PUT'])
def add_user_to_user_group(user_id, user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    UserGroupMemberService.create(user_id, user_group_id)
    return ok()

@bp.route('/user_groups/<int:user_group_id>/users/<int:user_id>', methods=['DELETE'])
def delete_user_from_user_group(user_id, user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    UserGroupMemberService.delete(user_id, user_group_id)
    return ok()

@bp.route('/users')
def get_users():
    users = current_app.config['PERM_USERS_GETTER']()
    return ok(users=users)

@bp.route('/users/<int:user_id>')
def get_user(user_id):
    user = current_app.config['PERM_USER_GETTER'](user_id)
    if not user:
        return not_found()
    return ok(user=user)
