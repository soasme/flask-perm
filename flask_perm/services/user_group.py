# -*- coding: utf-8 -*-
from sqlalchemy import func

from ..core import db
from ..models import UserGroup

def create(title, code=None):
    user_group = UserGroup(
        title=title,
        code=code,
    )
    db.session.add(user_group)
    db.session.commit()
    return user_group

def delete(id):
    user_group = UserGroup.query.get(id)
    if user_group:
        db.session.delete(user_group)
    db.session.commit()

def rename(id, title):
    user_group = UserGroup.query.get(id)
    user_group.title = title
    db.session.add(user_group)
    db.session.commit()
    return user_group

def update_code(id, code):
    user_group = UserGroup.query.get(id)
    user_group.code = code
    db.session.add(user_group)
    db.session.commit()
    return user_group

def get_by_code(code):
    return UserGroup.query.filter_by(code=code).first()

def get_user_groups_by_codes(codes):
    return UserGroup.query.filter(UserGroup.code.in_(codes)).all()

def get_user_groups():
    return UserGroup.query.all()

def get_user_groups_by_ids(ids):
    return UserGroup.query.filter(UserGroup.id.in_(ids)).all()

def rest(user_group):
    return dict(
        id=user_group.id,
        title=user_group.title,
        code=user_group.code,
    )

def get(id):
    return UserGroup.query.get(id)

def filter_user_groups(filter_by, offset, limit, sort_field='created_at', sort_dir='desc'):
    query = UserGroup.query
    if filter_by:
        query = query.filter_by(**filter_by)
    field = getattr(UserGroup, sort_field)
    order_by = getattr(field, sort_dir.lower())()
    return query.order_by(order_by).offset(offset).limit(limit).all()

def count_filter_user_group(filter_by, offset, limit):
    query = UserGroup.query
    if filter_by:
        query = query.filter_by(**filter_by)
    return query.value(func.count(UserGroup.id))

def get_all_user_group_ids():
    return [group.id for group in UserGroup.query.all()]
