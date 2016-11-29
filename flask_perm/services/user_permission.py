# -*- coding: utf-8 -*-
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..core import db
from ..models import UserPermission

def create(user_id, permission_id):
    user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission_id,
    )
    db.session.add(user_permission)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        user_permission = UserPermission.query.filter_by(
            user_id=user_id,
            permission_id=permission_id,
        ).first()
    return user_permission

def delete(user_permission_id):
    user_permission = UserPermission.query.get(user_permission_id)
    if user_permission:
        db.session.delete(user_permission)
    db.session.commit()

def get(id):
    return UserPermission.query.get(id)

def delete_by_user(user_id):
    user_permissions = UserPermission.query.filter_by(
        user_id=user_id
    ).all()
    for user_permission in user_permissions:
        db.session.delete(user_permission)
    db.session.commit()

def delete_by_permission(permission_id):
    user_permissions = UserPermission.query.filter_by(
        permission_id=permission_id,
    ).all()
    for user_permission in user_permissions:
        db.session.delete(user_permission)
    db.session.commit()

def get_users_by_permission(permission_id):
    rows = UserPermission.query.filter_by(
        permission_id=permission_id
    ).with_entities(
        UserPermission.user_id
    ).all()
    return [row.user_id for row in rows]

def get_permissions_by_user(user_id):
    rows = UserPermission.query.filter_by(
        user_id=user_id
    ).with_entities(
        UserPermission.permission_id
    ).all()
    return [row.permission_id for row in rows]

def filter_user_permissions(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = UserPermission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    field = getattr(UserPermission, sort_field)
    order_by = getattr(field, sort_dir.lower())()
    return query.order_by(order_by).offset(offset).limit(limit).all()

def count_filter_user_permission(filter_by, offset, limit):
    query = UserPermission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    return query.value(func.count(UserPermission.id))

def rest(user_permission):
    return dict(
        id=user_permission.id,
        user_id=user_permission.user_id,
        permission_id=user_permission.permission_id,
    )
