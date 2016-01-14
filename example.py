# -*- coding: utf-8 -*-
from collections import namedtuple
from flask import Flask, g, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_perm import Perm

app = Flask(__name__)
db = SQLAlchemy()
perm = Perm()
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flask_perm.db'
app.config['PERM_ADMIN_ECHO'] = True
app.config['PERM_ADMIN_USERNAME'] = 'admin'
app.config['PERM_ADMIN_PASSWORD'] = 'test'
app.config['PERM_SUPER_ADMIN_USER_IDS'] = [1]

db.app = app
db.init_app(app)
perm.app = app
perm.init_app(app)

class User(namedtuple('User', 'id nickname')):
    pass

@app.before_request
def before_request():
    g.user = User(**{'id': 1, 'nickname': 'user1'})

@perm.user_loader
def load_user(user_id):
    return User(**{'id': user_id, 'nickname': 'user%d' % user_id})

@perm.users_loader
def load_users(filter_by, sort_field, sort_dir, offset, limit):
    return [User(**{'id': id, 'nickname': 'user%d' % id}) for id in range(20)]

@perm.current_user_loader
def load_current_user():
    return g.user

@app.errorhandler(perm.Denied)
def permission_denied(e):
    return 'FORBIDDEN', 403

@app.route('/post/publish')
@perm.require_permission('post.publish')
def publish_post():
    return 'Hey, you can publish post!'

if __name__ == '__main__':
    app.run()
