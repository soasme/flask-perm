# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from ..core import get_db
from ..models import UserGroupMember

db = get_db()

def create(user_id, user_group_id):
    member = UserGroupMember(
        user_id=user_id,
        user_group_id=user_group_id,
    )
    db.session.add(member)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        member = UserGroupMember.query.filter_by(
            user_id=user_id,
            user_group_id=user_group_id,
        ).first()
    return member

def delete(user_id, user_group_id):
    member = UserGroupMember.query.filter_by(
        user_id=user_id,
        user_group_id=user_group_id,
    ).first()
    if member:
        db.session.delete(member)
    db.session.commit()

def get_users_by_group(user_group_id):
    rows = UserGroupMember.query.filter_by(
        user_group_id=user_group_id
    ).with_entities(
        UserGroupMember.user_id
    ).all()
    return [row.user_id for row in rows]

def get_user_groups_by_user(user_id):
    rows = UserGroupMember.query.filter_by(
        user_id=user_id
    ).with_entities(
        UserGroupMember.user_group_id
    ).all()
    return [row.user_group_id for row in rows]
