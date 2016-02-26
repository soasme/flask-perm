# -*- coding: utf-8 -*-

from flask import g
from pytest import raises

def test_get_require_permission_not_passed(perm):
    g.user = {'id': 1, 'is_allowed': False}
    f = lambda: True
    with raises(perm.Denied):
        perm.require_permission('code')(f)()

def test_get_require_permission_passed(perm):
    from flask_perm.services import PermissionService, UserPermissionService
    permission = PermissionService.create(
        'Test get_require_permission passed',
        'test.get_require_permission.passed'
    )
    UserPermissionService.create(user_id=1, permission_id=permission.id)

    g.user = {'id': 1, 'is_allowed': False}
    assert perm.require_permission('test.get_require_permission.passed')(lambda: True)()
    assert perm.require_permission_in_template('test.get_require_permission.passed')

def test_get_permissions(perm):
    from flask_perm.services import PermissionService, UserPermissionService
    permission = PermissionService.create(
        'Test get_permissions passed',
        'test_perm_app.test_get_permissions'
    )
    UserPermissionService.create(user_id=1, permission_id=permission.id)

    assert 'test_perm_app.test_get_permissions' in map(
        lambda p: p['code'], perm.get_user_permissions(1))
    assert perm.has_permission(1, 'test_perm_app.test_get_permissions')

def test_require_group_passed(perm):
    from flask_perm.services import UserGroupService, UserGroupMemberService
    user_group = UserGroupService.create(
        'Test require_group passed',
        'test.require_group_passed',
    )
    member = UserGroupMemberService.create(user_id=1, user_group_id=user_group.id)
    assert perm.require_group('test.require_group_passed')(lambda: True)()
    assert perm.require_group_in_template('test.require_group_passed')
    assert perm.require_group('*')(lambda: True)()

def test_require_group_failed(perm):
    from flask_perm.services import UserGroupService, UserGroupMemberService
    user_group = UserGroupService.create(
        'Test require_group failed',
        'test.require_group_failed',
    )
    member = UserGroupMemberService.create(user_id=2, user_group_id=user_group.id)
    with raises(perm.Denied):
        assert perm.require_group('test.require_group_passed')(lambda: True)()
    assert not perm.require_group_in_template('test.require_group_passed')
    with raises(perm.Denied):
        assert perm.require_group('*')(lambda: True)()
