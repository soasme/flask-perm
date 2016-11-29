# -*- coding: utf-8 -*-

import logging
import json
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from .core import db
from .services import (
    UserGroupService, PermissionService, UserGroupMemberService,
    UserPermissionService, UserGroupPermissionService,
    VerificationService,
)

bp = Blueprint('flask_perm_api', __name__)

def ok(data=None, count=1):
    response = jsonify(code=0, message='success', data=data)
    if count:
        response.headers['X-Total-Count'] = count
        return response
    return response

def bad_request(message='bad request', **data):
    return jsonify(code=1, message=message, data=data), 400

def not_found(message='not found', **data):
    return jsonify(code=1, message=message, data=data), 404

def forbidden(message='forbidden', **data):
    return jsonify(code=1, message=message, data=data), 403

def check_auth(username, password):
    return current_app.config['PERM_ADMIN_USERNAME'] == username and \
        current_app.config['PERM_ADMIN_PASSWORD'] == password

def current_perm():
    return current_app.extensions['perm']

def log_action(data, **kwargs):
    data = dict(data)
    data.update(kwargs)
    current_perm().log_admin_action(data)

@bp.before_request
def before_request():
    if not current_perm().has_perm_admin_logined():
        return forbidden()

@bp.errorhandler(IntegrityError)
def detect_integrity_error(e):
    return bad_request('conflict')

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
    log_action(permission, action='add', model='permission')
    return ok(permission)

def _get_filter_by():
    filter_by = request.args.get('_filters')
    if filter_by:
        try:
            filter_by = json.loads(filter_by)
        except ValueError:
            pass
    return filter_by

@bp.route('/permissions')
def get_permissions():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()

    permissions = PermissionService.filter_permissions(
        filter_by, offset, limit, sort_field, sort_dir)
    count = PermissionService.count_filter_permission(filter_by, offset, limit)

    permissions = map(PermissionService.rest, permissions)
    return ok(permissions, count)

@bp.route('/permissions/<int:permission_id>')
def get_permission(permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    permission = PermissionService.rest(permission)
    return ok(permission)

@bp.route('/permissions/<int:permission_id>', methods=['PUT'])
def update_permission(permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    if request.get_json().get('title'):
        PermissionService.rename(permission_id, request.get_json().get('title'))
    if request.get_json().get('code'):
        PermissionService.set_code(permission_id, request.get_json().get('code'))
    permission = PermissionService.rest(PermissionService.get(permission_id))
    log_action(permission, action='update', model='permission')
    return ok(permission)

@bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
def delete_permission(permission_id):
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    log_action(PermissionService.rest(permission), action='delete', model='permission')
    UserPermissionService.delete_by_permission(permission_id)
    UserGroupPermissionService.delete_by_permission(permission_id)
    PermissionService.delete(permission_id)
    return ok()

@bp.route('/user_permissions')
def get_user_permissions():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()

    user_permissions = UserPermissionService.filter_user_permissions(
        filter_by, offset, limit, sort_field, sort_dir)
    count = UserPermissionService.count_filter_user_permission(filter_by, offset, limit)

    user_permissions = map(UserPermissionService.rest, user_permissions)
    return ok(user_permissions, count)

@bp.route('/user_permissions', methods=['POST'])
def add_user_permission():
    data = request.get_json()
    try:
        permission_id = data['permission_id']
        user_id = data['user_id']
    except KeyError:
        return bad_request()

    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    user_permission = UserPermissionService.create(user_id, permission_id)
    user_permission = UserPermissionService.rest(user_permission)
    log_action(user_permission, action='add', model='user_permission')
    return ok(user_permission)

@bp.route('/user_permissions/<int:user_permission_id>', methods=['DELETE'])
def revoke_user_permission(user_permission_id):
    user_permission = UserPermissionService.get(user_permission_id)
    if not user_permission:
        return not_found()
    log_action(UserPermissionService.rest(user_permission), action='delete', model='user_permission')
    UserPermissionService.delete(user_permission_id)
    return ok()

@bp.route('/user_group_permissions')
def get_user_group_permissions():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()

    user_group_permissions = UserGroupPermissionService.filter_user_group_permissions(
        filter_by, offset, limit, sort_field, sort_dir)
    count = UserGroupPermissionService.count_filter_user_group_permissions(
        filter_by, offset, limit)

    user_group_permissions = map(UserGroupPermissionService.rest, user_group_permissions)
    return ok(user_group_permissions, count)

@bp.route('/user_group_permissions', methods=['POST'])
def add_user_group_permission():
    data = request.get_json()
    try:
        permission_id = data['permission_id']
        user_group_id = data['user_group_id']
    except KeyError:
        return bad_request()
    permission = PermissionService.get(permission_id)
    if not permission:
        return not_found()
    user_group_permission = UserGroupPermissionService.create(user_group_id, permission_id)
    user_group_permission = UserGroupPermissionService.rest(user_group_permission)
    log_action(user_group_permission, action='add', model='user_permission')
    return ok(user_group_permission)

@bp.route('/user_group_permissions/<int:user_group_permission_id>', methods=['DELETE'])
def revoke_user_group_permission(user_group_permission_id):
    user_group_permission = UserGroupPermissionService.get(user_group_permission_id)
    if not user_group_permission:
        return not_found()
    log_action(UserGroupPermissionService.rest(user_group_permission),
               action='delete', model='user_group_permission')
    UserGroupPermissionService.delete(user_group_permission_id)
    return ok()

@bp.route('/user_groups', methods=['POST'])
def add_user_group():
    try:
        data = request.get_json()
        title = data['title']
        code = data['code']
    except KeyError:
        return bad_request()
    user_group = UserGroupService.create(title, code)
    user_group = UserGroupService.rest(user_group)
    log_action(user_group, action='add', model='user_group')
    return ok(user_group)

@bp.route('/user_groups')
def get_user_groups():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()

    user_groups = UserGroupService.filter_user_groups(
        filter_by, offset, limit, sort_field, sort_dir)
    count = UserGroupService.count_filter_user_group(filter_by, offset, limit)

    user_groups = map(UserGroupService.rest, user_groups)
    return ok(user_groups, count)

@bp.route('/user_groups/<int:user_group_id>')
def get_user_group(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    user_group = UserGroupService.rest(user_group)
    return ok(user_group)

@bp.route('/user_groups/<int:user_group_id>', methods=['PUT'])
def update_user_group(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    data = request.get_json()
    if 'title' in data and data['title']:
        UserGroupService.rename(user_group_id, data['title'])
    if 'code' in data and data['code']:
        UserGroupService.update_code(user_group_id, data['code'])
    user_group = UserGroupService.rest(UserGroupService.get(user_group_id))
    log_action(user_group, action='update', model='user_group')
    return ok(user_group)

@bp.route('/user_groups/<int:user_group_id>', methods=['DELETE'])
def delete_user_group(user_group_id):
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    log_action(UserGroupService.rest(user_group), action='delete', model='user_group')
    UserGroupPermissionService.delete_by_user_group(user_group_id)
    UserGroupService.delete(user_group_id)
    return ok()

@bp.route('/user_group_members')
def get_user_group_members():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()

    members = UserGroupMemberService.filter_user_group_members(
        filter_by, offset, limit, sort_field, sort_dir)
    count = UserGroupMemberService.count_filter_user_group_members(filter_by, offset, limit)

    members = map(UserGroupMemberService.rest, members)
    return ok(members, count)

@bp.route('/user_group_members', methods=['POST'])
def add_user_group_member():
    data = request.get_json()
    try:
        user_id = data['user_id']
        user_group_id = data['user_group_id']
    except KeyError:
        return bad_request()
    user_group = UserGroupService.get(user_group_id)
    if not user_group:
        return not_found()
    member = UserGroupMemberService.create(user_id, user_group_id)
    member = UserGroupMemberService.rest(member)
    log_action(member, action='add', model='user_group_member')
    return ok(member)

@bp.route('/user_group_members/<int:user_group_member_id>', methods=['DELETE'])
def delete_user_from_user_group(user_group_member_id):
    user_group_member = UserGroupMemberService.get(user_group_member_id)
    if not user_group_member:
        return not_found()
    log_action(UserGroupMemberService.rest(user_group_member), action='delete', model='user_group_member')
    UserGroupMemberService.delete(user_group_member_id)
    return ok()

def jsonify_user(user):
    return dict(id=user.id, nickname=user.nickname)

@bp.route('/users')
def get_users():
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    sort_field = request.args.get('_sortField', 'created_at').lower()
    sort_dir = request.args.get('_sortDir', 'DESC').lower()
    filter_by = _get_filter_by()
    users = current_perm().load_users(filter_by, sort_field, sort_dir, offset, limit)
    users = map(jsonify_user, users)
    return ok(users)

@bp.route('/users/<int:user_id>')
def get_user(user_id):
    user = current_perm().load_user(user_id)
    if not user:
        return not_found()
    return ok(jsonify_user(user))
