# -*- coding: utf-8 -*-

from datetime import datetime

from .core import db

class SuperAdmin(db.Model):

    __tablename__ = 'perm_super_admin'
    __table_args__ = (
        db.UniqueConstraint('email', name='ux_super_admin_email'),
    )

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Permission(db.Model):

    __tablename__ = 'perm_permission'
    __table_args__ = (
        db.UniqueConstraint('code', name='ux_permission_code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), default='', nullable=False)
    code = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return '<Permission id={.id} title={.title} code={.code}>'.format(self)

class UserGroup(db.Model):

    __tablename__ = 'perm_user_group'
    __table_args__ = (
        db.UniqueConstraint('code', name='ux_user_group_code'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), default='', nullable=False)
    code = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return '<UserGroup id={.id} title={.title} code={.code}>'.format(self)

class UserGroupMember(db.Model):

    __tablename__ = 'perm_user_group_member'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'user_group_id', name='ux_user_in_user_group'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_group_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return '<UserGroupMember id={.id} user_id={.user_id} user_group_id={.user_group_id}>'.format(self)

class UserPermission(db.Model):

    __tablename__ = 'perm_user_permission'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='ux_user_permission'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    permission_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return '<UserPermission id={.id} user_id={.user_id} permission_id={.permission_id}>'.format(self)

class UserGroupPermission(db.Model):

    __tablename__ = 'perm_user_group_permission'
    __table_args__ = (
        db.UniqueConstraint('user_group_id', 'permission_id', name='ux_user_permission'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_group_id = db.Column(db.Integer, nullable=False)
    permission_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __str__(self):
        return '<UserGroupPermission id={.id} user_id={.user_id} permission_id={.permission_id}>'.format(self)
