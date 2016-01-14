# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, url_for, redirect, request, flash

bp = Blueprint('perm-admin', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    if not bp.perm.has_perm_admin_logined():
        return redirect(url_for('perm-admin.login'))

    render_data = {
        'base_api_url': current_app.config.get('PERM_ADMIN_API_PREFIX'),
        'base_web_url': current_app.config.get('PERM_ADMIN_PREFIX'),
        'debug': current_app.config.get('DEBUG'),
    }

    return render_template('/perm-admin/index.html', **render_data)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if bp.perm.check_perm_admin_auth(username, password):
            bp.perm.login_perm_admin()
            return redirect(url_for('perm-admin.index'))
        else:
            flash(u'Invalid Password', 'error')
            return redirect(url_for('perm-admin.login'))
    return render_template('/perm-admin/login.html')

@bp.route('/logout')
def logout():
    bp.perm.logout_perm_admin()
    return redirect(url_for('perm-admin.login'))
