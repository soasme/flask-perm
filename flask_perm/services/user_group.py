# -*- coding: utf-8 -*-

from ..core import get_db
from ..models import UserGroup

db = get_db()

def create(title):
    user_group = UserGroup(
        title=title
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

def get_user_groups():
    return UserGroup.query.all()

def get_user_groups_by_ids(ids):
    return UserGroup.query.filter(UserGroup.id.in_(ids)).all()

def rest(user_group):
    return dict(
        id=user_group.id,
        title=user_group.title,
    )

def get(id):
    return UserGroup.query.get(id)
