# -*- coding: utf-8 -*-

from ..core import get_db
from ..models import Permission

db = get_db()

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

def get_permissions_by_ids(ids):
    return Permission.query.filter(Permission.id.in_(ids)).all()

def get_by_code(code):
    return Permission.query.filter_by(code=code).first()
