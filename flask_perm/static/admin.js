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
  nga.configure(admin);
}]);
