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
