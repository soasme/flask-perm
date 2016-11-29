# -*- coding: utf-8 -*-
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..core import db
from ..models import UserGroupPermission

def create(user_group_id, permission_id):
    user_group_permission = UserGroupPermission(
        user_group_id=user_group_id,
        permission_id=permission_id,
    )
    db.session.add(user_group_permission)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        user_group_permission = UserGroupPermission.query.filter_by(
            user_group_id=user_group_id,
            permission_id=permission_id,
        ).first()
    return user_group_permission

def get(id):
    return UserGroupPermission.query.get(id)

def delete(id):
    user_group_permission = UserGroupPermission.query.get(id)
    if user_group_permission:
        db.session.delete(user_group_permission)
    db.session.commit()

def delete_by_permission(permission_id):
    user_group_permissions = UserGroupPermission.query.filter_by(
        permission_id=permission_id
    ).all()
    for user_group_permission in user_group_permissions:
        db.session.delete(user_group_permission)
    db.session.commit()

def delete_by_user_group(user_group_id):
    user_group_permissions = UserGroupPermission.query.filter_by(
        user_group_id=user_group_id,
    ).all()
    for user_group_permission in user_group_permissions:
        db.session.delete(user_group_permission)
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

def filter_user_group_permissions(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = UserGroupPermission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    field = getattr(UserGroupPermission, sort_field)
    order_by = getattr(field, sort_dir.lower())()
    return query.order_by(order_by).offset(offset).limit(limit).all()

def count_filter_user_group_permissions(filter_by, offset, limit):
    query = UserGroupPermission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    return query.value(func.count(UserGroupPermission.id))

def rest(user_permission):
    return dict(
        id=user_permission.id,
        user_group_id=user_permission.user_group_id,
        permission_id=user_permission.permission_id,
    )
