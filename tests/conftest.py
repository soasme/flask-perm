# -*- coding: utf-8 -*-

from pytest import fixture
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_perm import Perm

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

@fixture
def db(app, request):
    perm_db = SQLAlchemy()
    perm_db.app = app
    perm_db.init_app(app)
    return perm_db

@fixture
def perm(app, db, request):
    app.config['PERM_DB'] = db
    app.config['PERM_USER_GETTER'] = lambda id: {'id': id, 'nickname': 'User%d' % id}
    app.config['PERM_USERS_GETTER'] = lambda: [
        app.config['PERM_USER_GETTER'](id) for id in range(20)
    ]
    g.user = {'id': 1, 'nickname': 'User1', 'is_allowed': True}
    app.config['PERM_CURRENT_USER_GETTER'] = lambda: g.user
    app.config['PERM_CURRENT_USER_ACCESS_VALIDATOR'] = lambda: g.user['is_allowed']
    app.config['PERM_URL_PREFIX'] = '/perm'
    perm = Perm()
    perm.app = app
    perm.init_app(app)
    db.create_all()
    return perm
