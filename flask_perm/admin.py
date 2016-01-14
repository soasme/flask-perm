# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, abort, url_for, redirect, request, flash
from flask_login import login_user, logout_user

bp = Blueprint('perm-admin', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    if not bp.perm.has_perm_admin_logined():
        return redirect(url_for('perm-admin.login'))
    render_data = {
    }

    return render_template('/perm-admin/index.html', **render_data)
