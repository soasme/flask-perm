# -*- coding: utf-8 -*-

from flask import current_app
from flask.ext.script import Manager, prompt_pass, prompt_bool
from flask_perm.services import SuperAdminService

perm_manager = Manager(usage="Perform permission operations")


@perm_manager.command
@perm_manager.option('-e', '--email', help='Super admin email')
def create_superadmin(email):
    password = prompt_pass('Please input password')
    confirm_password = prompt_pass('Please input password again')
    if password != confirm_password:
        print('Password mismatch! Please confirm that you type same passwords.')
        return
    current_app.extensions['perm'].create_super_admin(email, password)
    print('Success!')

@perm_manager.command
@perm_manager.option('-e', '--email', help='Super admin email')
def delete_superadmin(email):
    super_admin = SuperAdminService.get_by_email(email)
    if not super_admin:
        print('Super admin not found!')
        return
    if prompt_bool('Do you really want to delete this account? [y/n]'):
        SuperAdminService.delete(super_admin.id)
        print('Success!')

@perm_manager.command
def list_superadmin():
    superadmins = map(SuperAdminService.to_dict, SuperAdminService.list())
    for superadmin in superadmins:
        print(superadmin['email'])
