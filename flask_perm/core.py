# -*- coding: utf-8 -*-


from werkzeug.utils import import_string
from flask import _app_ctx_stack as stack
from flask_sqlalchemy import SQLAlchemy

def get_db():
    ctx = stack.top
    if ctx is None or not hasattr(ctx, 'perm_db'):
        raise Exception('Flask-Perm extension has not been initialized.')
    return ctx.perm_db

def init_db(db):
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'perm_db'):
            if isinstance(db, SQLAlchemy):
                ctx.perm_db = db
            elif isinstance(db, str):
                ctx.perm_db = import_string(db)
            else:
                raise Exception('Unknown db')
