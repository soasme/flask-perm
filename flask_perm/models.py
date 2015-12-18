# -*- coding: utf-8 -*-

from datetime import datetime

from .core import get_db

db = get_db()

class Permission(db.Model):

    __tablename__ = 'permission'
    __table_args__ = (
        db.UniqueConstraint('code', name='ux_permission_code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), default='', nullable=False)
    code = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UserGroup(db.Model):

    __tablename__ = 'user_group'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), default='', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UserGroupMember(db.Model):

    __tablename__ = 'user_group_member'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'user_group_id', name='ux_user_in_user_group'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_group_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UserPermission(db.Model):

    __tablename__ = 'user_permission'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='ux_user_permission'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    permission_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UserGroupPermission(db.Model):

    __tablename__ = 'user_group_permission'
    __table_args__ = (
        db.UniqueConstraint('user_group_id', 'permission_id', name='ux_user_permission'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_group_id = db.Column(db.Integer, nullable=False)
    permission_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
