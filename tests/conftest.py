# -*- coding: utf-8 -*-

from collections import namedtuple

from pytest import fixture
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_perm import Perm
from flask_perm.core import db

@fixture
def app(request):
    flask_app = Flask(__name__)
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = True
    flask_app.config['SERVER_NAME'] = 'localhost'
    ctx = flask_app.app_context()
    ctx.push()
    request.addfinalizer(ctx.pop)
    return flask_app

class User(namedtuple('User', 'id nickname')):
    pass

@fixture
def perm(app, request):
    def user_loader(id):
        return User(id=id, nickname='User%d'%id)

    def current_user_loader():
        return user_loader(1)

    def users_loader(**kwargs):
        return [user_loader(id) for id in range(20)]

    app.config['PERM_URL_PREFIX'] = '/perm'
    app.config['PERM_ADMIN_USERNAME'] = 'admin'
    app.config['PERM_ADMIN_PASSWORD'] = 'test'

    perm = Perm()
    perm.app = app
    perm.init_app(app)
    perm.user_loader(user_loader)
    perm.current_user_loader(current_user_loader)
    perm.users_loader(users_loader)

    db.create_all()
    return perm
