# -*- coding: utf-8 -*-

from ..core import db, bcrypt
from ..models import SuperAdmin

def create(email, password):
    super_admin = SuperAdmin(
        email=email,
        password=bcrypt.generate_password_hash(password)
    )
    db.session.add(super_admin)
    db.session.commit()
    return super_admin

def to_dict(obj):
    return dict(
        id=obj.id,
        email=obj.email,
    )

def verify_password(email, password):
    super_admin = get_by_email(email)
    if not super_admin:
        return False
    if not bcrypt.check_password_hash(super_admin.password, password):
        return False
    return True

def delete(id):
    super_admin = get(id)
    if super_admin:
        db.session.delete(super_admin)
    db.session.commit()

def reset_password(id, password):
    super_admin = get(id)
    if super_admin:
        super_admin.password = bcrypt.generate_password_hash(password)
        db.session.add(super_admin)
    db.session.commit()
    return super_admin

def get(id):
    return SuperAdmin.query.get(id)

def get_by_email(email):
    return SuperAdmin.query.filter_by(email=email).first()

def list():
    return SuperAdmin.query.all()
