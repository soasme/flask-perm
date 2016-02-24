# -*- coding: utf-8 -*-

import json
import base64
from functools import partial
from pytest import fixture
from flask import url_for
from flask_perm.services import SuperAdminService

class Client(object):

    def __init__(self, app, current_user=None):
        self.app = app
        self.current_user = current_user

    @property
    def client(self):
        return self.app.test_client()

    def request(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})
        code = '%s:%s' % (
            'admin@example.org',
            'test'
        )
        headers['Authorization'] = 'Basic ' + base64.b64encode(code)
        kwargs['headers'] = headers
        return self.client.open(url, method=method, **kwargs)

    def __getattr__(self, method):
        return partial(self.request, method)

@fixture
def super_admin(app, perm):
    return SuperAdminService.create('admin@example.org', 'test')

@fixture
def client(app, perm, super_admin):
    return Client(app, super_admin)


@fixture
def permission(request, client):
    code = '%s.%s' % (request.module.__name__, request.function.__name__)
    resp = client.post(
        url_for('flask_perm_api.add_permission'),
        data=json.dumps(dict(title='Test Permission', code=code)),
        content_type='application/json',
    )
    return json.loads(resp.data)['data']

@fixture
def user_group(request, client):
    code = 'code.%s.%s' % (request.module.__name__, request.function.__name__)
    resp = client.post(
        url_for('flask_perm_api.add_user_group'),
        data=json.dumps(dict(title='Test UserGroup', code=code)),
        content_type='application/json',
    )
    return json.loads(resp.data)['data']

def test_add_permission(permission):
    assert permission['id']
    assert permission['title'] == 'Test Permission'
    assert permission['code'] == 'tests.test_blueprint.test_add_permission'

def test_get_permissions(client, permission):
    resp = client.get(url_for('flask_perm_api.get_permissions'))
    assert resp.status_code == 200
    assert permission in json.loads(resp.data)['data']

def test_filter_permission_by_id0(client, permission):
    resp = client.get(url_for('flask_perm_api.get_permissions'), query_string={
        '_filters': '{"id": 0}',
    })
    assert resp.status_code == 200
    assert not json.loads(resp.data)['data']

def test_filter_permission_by_permission_id(client, permission):
    resp = client.get(url_for('flask_perm_api.get_permissions'), query_string={
        '_filters': '{"id": %s}' % permission['id'],
    })
    assert resp.status_code == 200
    assert permission in json.loads(resp.data)['data']

def test_get_permission(client, permission):
    resp = client.get(
        url_for(
            'flask_perm_api.get_permission',
            permission_id=permission['id']
        )
    )
    assert resp.status_code == 200
    assert permission == json.loads(resp.data)['data']

def test_update_permission(client, permission):
    resp = client.put(
        url_for(
            'flask_perm_api.update_permission',
            permission_id=permission['id'],
        ),
        data=json.dumps(dict(title='Test Permission!', code='test_blueprint.test_update_permission!')),
        content_type='application/json',
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['data']['id']
    assert data['data']['title'] == 'Test Permission!'
    assert data['data']['code'] == 'test_blueprint.test_update_permission!'



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

def add_user_permission(client, user_id, permission_id):
    return client.post(
        url_for(
            'flask_perm_api.add_user_permission',
        ),
        data=json.dumps(dict(
            user_id=user_id,
            permission_id=permission_id
        )),
        content_type='application/json',
    )

def add_user_group_member(client, user_id, user_group_id):
    return client.post(
        url_for(
            'flask_perm_api.add_user_group_member',
        ),
        data=json.dumps(dict(
            user_id=user_id,
            user_group_id=user_group_id,
        )),
        content_type='application/json',
    )

def add_user_group_permission(client, user_group_id, permission_id):
    return client.post(
        url_for(
            'flask_perm_api.add_user_group_permission',
        ),
        data=json.dumps(dict(
            user_group_id=user_group_id,
            permission_id=permission_id
        )),
        content_type='application/json',
    )

def test_add_user_permission(client, permission, perm):
    resp = add_user_permission(client, 1, permission['id'])
    assert resp.status_code == 200
    assert perm.has_permission(1, 'tests.test_blueprint.test_add_user_permission')

def test_revoke_user_permission(client, perm, permission):
    resp = add_user_permission(client, 1, permission['id'])
    id = json.loads(resp.data)['data']['id']
    resp = client.delete(
        url_for(
            'flask_perm_api.revoke_user_permission',
            user_permission_id=id,
        )
    )
    assert resp.status_code == 200
    assert not perm.has_permission(1, 'tests.test_blueprint.test_revoke_user_permission')

def test_add_user_group_permissions(client, permission, user_group):
    resp = add_user_group_permission(client, user_group['id'], permission['id'])
    assert resp.status_code == 200

def test_revoke_user_group_permissions(client, permission, user_group):
    resp = add_user_group_permission(client, user_group['id'], permission['id'])
    id = json.loads(resp.data)['data']['id']
    resp = client.delete(
        url_for(
            'flask_perm_api.revoke_user_group_permission',
            user_group_permission_id=id,
        )
    )
    assert resp.status_code == 200

def test_get_user_permissions_by_user_id(client, permission):
    resp = add_user_permission(client, 1, permission['id'])
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_permissions',
        ),
        query_string={'_filters': '{"user_id":1}'}
    )
    assert resp.status_code ==200
    assert json.loads(resp.data)['data']

def test_get_user_permissions_by_permission_id(client, permission):
    resp = add_user_permission(client, 1, permission['id'])
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_permissions',
        ),
        query_string={'_filters': '{"permission_id":%s}' % permission['id']}
    )
    assert resp.status_code ==200
    assert json.loads(resp.data)['data']

def test_get_user_group_permissions_by_user_id(client, permission):
    resp = add_user_group_permission(client, 1, permission['id'])
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_group_permissions',
        ),
        query_string={'_filters': '{"user_group_id":1}'}
    )
    assert resp.status_code ==200
    assert json.loads(resp.data)['data']

def test_get_user_group_permissions_by_permission_id(client, permission):
    resp = add_user_group_permission(client, 1, permission['id'])
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_group_permissions',
        ),
        query_string={'_filters': '{"permission_id":%s}' % permission['id']}
    )
    assert resp.status_code ==200
    assert json.loads(resp.data)['data']

def test_add_user_group(client, user_group):
    assert user_group['id']

def test_get_user_groups(client, user_group):
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_groups'
        )
    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']

def test_update_user_group(client, user_group):
    resp = client.put(
        url_for(
            'flask_perm_api.update_user_group',
            user_group_id=user_group['id'],
        ),
        data=json.dumps(dict(title='updated')),
        content_type='application/json'
    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']['title'] == 'updated'

def test_delete_user_group(client, user_group):
    resp = client.delete(
        url_for(
            'flask_perm_api.delete_user_group',
            user_group_id=user_group['id'],
        ),
    )
    assert resp.status_code == 200

def test_add_user_to_user_group(client, user_group):
    resp = add_user_group_member(client, 1, user_group['id'])
    assert resp.status_code == 200

def test_delete_user_from_user_group(client, user_group):
    resp = add_user_group_member(client, 1, user_group['id'])
    id = json.loads(resp.data)['data']['id']
    resp = client.delete(
        url_for(
            'flask_perm_api.delete_user_from_user_group',
            user_group_member_id=id
        )
    )
    assert resp.status_code == 200

def test_get_user_group_members(client, user_group):
    add_user_group_member(client, 1, user_group['id'])
    resp = client.get(
        url_for(
            'flask_perm_api.get_user_group_members',
        ),
        query_string={
            '_filters': '{"user_group_id":%s}' % user_group['id'],
        }

    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']

def test_get_users(client):
    resp = client.get(url_for('flask_perm_api.get_users'))
    assert resp.status_code == 200
    assert isinstance(json.loads(resp.data)['data'], list)

def test_get_user(client):
    resp = client.get(url_for('flask_perm_api.get_user', user_id=1))
    assert resp.status_code == 200
    assert json.loads(resp.data)['data']['id'] == 1
