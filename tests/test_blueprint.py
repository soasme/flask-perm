# -*- coding: utf-8 -*-

import json

from pytest import fixture
from flask import url_for

@fixture
def client(app, perm):
    return app.test_client()

@fixture
def permission(request, client):
    code = '%s.%s' % (request.module.__name__, request.function.__name__)
    resp = client.post(
        url_for('flask_perm_api.add_permission'),
        data=json.dumps(dict(title='Test Permission', code=code)),
        content_type='application/json',
    )
    return json.loads(resp.data)['data']['permission']

@fixture
def user_group(client):
    resp = client.post(
        url_for('flask_perm_api.add_user_group'),
        data=json.dumps(dict(title='Test UserGroup')),
        content_type='application/json',
    )
    return json.loads(resp.data)['data']['user_group']

def test_add_permission(permission):
    assert permission['id']
    assert permission['title'] == 'Test Permission'
    assert permission['code'] == 'tests.test_blueprint.test_add_permission'

def test_get_permissions(client, permission):
    resp = client.get(url_for('flask_perm_api.get_permissions'))
    assert resp.status_code == 200
    assert permission in json.loads(resp.data)['data']['permissions']

def test_get_permission(client, permission):
    resp = client.get(
        url_for(
            'flask_perm_api.get_permission',
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200
    assert permission == json.loads(resp.data)['data']['permission']

def test_update_permission(client, permission):
    resp = client.patch(
        url_for(
            'flask_perm_api.update_permission',
            permission_id=permission['id'],
        ),
        data=json.dumps(dict(title='Test Permission!', code='test_blueprint.test_update_permission!')),
        content_type='application/json',
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['data']['permission']['id']
    assert data['data']['permission']['title'] == 'Test Permission!'
    assert data['data']['permission']['code'] == 'test_blueprint.test_update_permission!'



def test_delete_permission(client, permission):
    resp = client.delete(
        url_for(
            'flask_perm_api.delete_permission',
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200
    resp = client.get(
        url_for(
            'flask_perm_api.get_permission',
            permission_id=permission['id']
        ),
    )
    assert resp.status_code == 404

def test_add_user_permission(client, permission, perm):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_permission',
            user_id=1,
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200
    assert perm.has_permission(1, 'tests.test_blueprint.test_add_user_permission')

def test_revoke_user_permission(client, perm, permission):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_permission',
            user_id=1,
            permission_id=permission['id']
        )
    )
    resp = client.delete(
        url_for(
            'flask_perm_api.revoke_user_permission',
            user_id=1,
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200
    assert not perm.has_permission(1, 'tests.test_blueprint.test_revoke_user_permission')

def test_add_user_group_permissions(client, permission, user_group):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_group_permission',
            user_group_id=user_group['id'],
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200


def test_revoke_user_group_permissions(client, permission, user_group):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_group_permission',
            user_group_id=user_group['id'],
            permission_id=permission['id']
        )
    )
    resp = client.delete(
        url_for(
            'flask_perm_api.revoke_user_group_permission',
            user_group_id=user_group['id'],
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200

def test_get_user_permissions(client, permission):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_permission',
            user_id=1,
            permission_id=permission['id']
        )
    )
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_permissions',
            user_id=1
        )
    )
    assert resp.status_code ==200
    assert json.loads(resp.data)['data']['permissions']

def test_add_user_group(client, user_group):
    assert user_group['id']

def test_get_user_groups(client, user_group):
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_groups'
        )
    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']['user_groups']

def test_update_user_group(client, user_group):
    resp = client.patch(
        url_for(
            'flask_perm_api.update_user_group',
            user_group_id=user_group['id'],
        ),
        data=json.dumps(dict(title='updated')),
        content_type='application/json'
    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']['user_group']['title'] == 'updated'

def test_delete_user_group(client, user_group):
    resp = client.delete(
        url_for(
            'flask_perm_api.delete_user_group',
            user_group_id=user_group['id'],
        ),
    )
    assert resp.status_code == 200

def test_add_user_to_user_group(client, user_group):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_to_user_group',
            user_id=1,
            user_group_id=user_group['id'],
        )
    )
    assert resp.status_code == 200

def test_delete_user_from_user_group(client, user_group):
    resp = client.put(
        url_for(
            'flask_perm_api.add_user_to_user_group',
            user_id=1,
            user_group_id=user_group['id'],
        )
    )
    resp = client.delete(
        url_for(
            'flask_perm_api.delete_user_from_user_group',
            user_id=1,
            user_group_id=user_group['id'],
        )
    )
    assert resp.status_code == 200

def test_get_user_group_members(client, user_group):
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_group_members',
            user_group_id=user_group['id']
        )
    )
    assert resp.status_code == 200
    assert isinstance(json.loads(resp.data)['data']['users'], list)

def test_get_users(client):
    resp = client.get(url_for('flask_perm_api.get_users'))
    assert resp.status_code == 200
    assert isinstance(json.loads(resp.data)['data']['users'], list)

def test_get_user(client):
    resp = client.get(url_for('flask_perm_api.get_user', user_id=1))
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']['user']['id'] == 1
