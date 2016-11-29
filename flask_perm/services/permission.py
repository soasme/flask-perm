# -*- coding: utf-8 -*-
from sqlalchemy import func

from ..core import db
from ..models import Permission

def create(title, code=None):
    permission = Permission(
        title=title,
        code=code
    )
    db.session.add(permission)
    db.session.commit()
    return permission

def delete(id):
    permission = Permission.query.get(id)
    if permission:
        db.session.delete(permission)
    db.session.commit()

def rename(id, title):
    permission = Permission.query.get(id)
    permission.title = title
    db.session.add(permission)
    db.session.commit()
    return permission

def rest(permission):
    return dict(
        id=permission.id,
        title=permission.title,
        code=permission.code
    )

def set_code(id, code):
    permission = Permission.query.get(id)
    permission.code = code
    db.session.add(permission)
    db.session.commit()
    return permission

def get(id):
    return Permission.query.get(id)

def get_permissions():
    return Permission.query.all()

def filter_permissions(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = Permission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    field = getattr(Permission, sort_field)
    order_by = getattr(field, sort_dir.lower())()
    return query.order_by(order_by).offset(offset).limit(limit).all()

def count_filter_permission(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = Permission.query
    if filter_by:
        query = query.filter_by(**filter_by)
    return query.value(func.count(Permission.id))


def get_permissions_by_ids(ids):
    return Permission.query.filter(Permission.id.in_(ids)).all()

def get_by_code(code):
    return Permission.query.filter_by(code=code).first()
