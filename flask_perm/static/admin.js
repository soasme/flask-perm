// declare a new module called 'myApp', and make it require the `ng-admin` module as a dependency
var PermAdmin = angular.module('PermAdmin', ['ng-admin']);
// declare a function to run when the module bootstraps (during the 'config' phase)
PermAdmin.config(['NgAdminConfigurationProvider', function (nga) {
  // create an admin application
  var applicationName = 'Permission Management Admininistration';
  var admin = nga.application(
    applicationName,
  ).baseApiUrl(window.g.baseApiUrl);
  // more configuration here later
  nga.configure(admin);
}]);
