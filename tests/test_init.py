# -*- coding: utf-8 -*-

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_perm.core import get_db

def test_perm_init_db(perm):
    assert get_db()

def test_perm_get_db_will_throw_error_when_not_init_db():
    pytest.raises(Exception, get_db)
