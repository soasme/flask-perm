# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError

from ..core import get_db
from ..models import UserPermission

db = get_db()

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

def delete(user_id, permission_id):
    user_permission = UserPermission.query.filter_by(
        user_id=user_id,
        permission_id=permission_id
    ).first()
    if user_permission:
        db.session.delete(user_permission)
    db.session.commit()

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
