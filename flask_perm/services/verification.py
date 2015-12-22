# -*- coding: utf-8 -*-

from ..core import db
from .user_permission import (
    get_permissions_by_user,
    delete_by_user as delete_user_permissions_by_user,
)
from .user_group_permission import get_permissions_by_user_group
from .user_group_member import get_user_groups_by_user

def get_user_group_permissions_by_user(user_id):
    user_permission_ids = set()
    user_group_ids = get_user_groups_by_user(user_id)
    for user_group_id in user_group_ids:
        user_group_permission_ids = set(get_permissions_by_user_group(user_group_id))
        user_permission_ids.update(user_group_permission_ids)
    return user_permission_ids

def get_user_permissions(user_id):
    user_permission_ids = set(get_permissions_by_user(user_id))
    user_group_permission_ids = get_user_group_permissions_by_user(user_id)
    return user_permission_ids | user_group_permission_ids

def has_permission(user_id, permission_id):
    return permission_id in get_user_permissions(user_id)
