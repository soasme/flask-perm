// declare a new module called 'myApp', and make it require the `ng-admin` module as a dependency
var PermAdmin = angular.module('PermAdmin', ['ng-admin']);
// declare a function to run when the module bootstraps (during the 'config' phase)
PermAdmin.config(['NgAdminConfigurationProvider', function (nga) {
  // create an admin application
  var applicationName = 'Permission Management Admininistration';
  var admin = nga.application(
    applicationName,
    window.g.debug
  ).baseApiUrl(window.g.baseApiUrl);
  // more configuration here later
  var permission = nga.entity('permissions');
  var user = nga.entity('users').readOnly();
  var userGroup = nga.entity('user_groups');
  var userPermission = nga.entity('user_permissions');
  var userGroupMember = nga.entity('user_group_members');
  var userGroupPermission = nga.entity('user_group_permissions');
  var fields = {
    title: nga.field('title').label('Title'),
    code: nga.field('code').label('Code'),
    nickname: nga.field('nickname').label('Nickname'),
    user: nga.field('user_id', 'reference')
      .targetEntity(user)
      .targetField(nga.field('nickname'))
      .label('User'),
    userGroup: nga.field('user_group_id', 'reference')
      .targetEntity(userGroup)
      .targetField(nga.field('title'))
      .label('User Group'),
    permission: nga.field('permission_id', 'reference')
      .targetEntity(permission)
      .targetField(nga.field('title'))
      .label('Permission')
  };

  admin.addEntity(permission);
  admin.addEntity(userGroup);
  admin.addEntity(user);
  admin.addEntity(userPermission);
  admin.addEntity(userGroupPermission);
  admin.addEntity(userGroupMember);

  permission.listView().fields([
    fields.title.isDetailLink(true),
    fields.code,
  ]).filters([
    fields.title,
    fields.code,
  ]);

  permission.creationView().fields([
    fields.title.validation({ required: true}),
    fields.code.validation({ required: true}),
  ]);

  permission.editionView().fields(permission.creationView().fields());

  userGroup.listView().fields([
    fields.title.isDetailLink(true),
    fields.code,
  ]);

  userGroup.creationView().fields([
    fields.title.validation({ required: true }),
    fields.code.validation({ required: true }),
  ]);

  userGroup.editionView().fields(userGroup.creationView().fields());

  nga.configure(admin);
}]);
