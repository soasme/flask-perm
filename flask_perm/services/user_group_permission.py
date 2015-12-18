# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError

from ..core import get_db
from ..models import UserGroupPermission

db = get_db()

def create(user_group_id, permission_id):
    user_permission = UserGroupPermission(
        user_group_id=user_group_id,
        permission_id=permission_id,
    )
    db.session.add(user_permission)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        user_permission = UserGroupPermission.query.filter_by(
            user_group_id=user_group_id,
            permission_id=permission_id,
        ).first()
    return user_permission

def delete(user_group_id, permission_id):
    user_permission = UserGroupPermission.query.filter_by(
        user_group_id=user_group_id,
        permission_id=permission_id
    ).first()
    if user_permission:
        db.session.delete(user_permission)
    db.session.commit()

def get_user_groups_by_permission(permission_id):
    rows = UserGroupPermission.query.filter_by(
        permission_id=permission_id
    ).with_entities(
        UserGroupPermission.user_group_id
    ).all()
    return [row.user_group_id for row in rows]

def get_permissions_by_user_group(user_group_id):
    rows = UserGroupPermission.query.filter_by(
        user_group_id=user_group_id
    ).with_entities(
        UserGroupPermission.permission_id
    ).all()
    return [row.permission_id for row in rows]
