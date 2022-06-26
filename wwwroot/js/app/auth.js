
app.controller('AuthController', function ($rootScope, $scope, $log, $http, $location, Auth, Alerts, LSM, Node) {

  // Auth defaults
  $scope.AuthForm = {
    Data: { Username: null, Password: null },
    Submit: false
  };


  $scope.Login = function(AuthForm) {
    AuthForm.Submit = true;
    var AuthData = {
      username: AuthForm.Data.Username,
      password: AuthForm.Data.Password
    }
    Auth.Login(AuthData)
    .then(
      function(success) {
        $log.debug('Login: CurrentUser', $rootScope.CurrentUser);
        // Check node activation
        Node.Service('activate').then(function(success) {}, function(error) {});
        // Load GUI from localStogare.<username> or GUI defaults
        $rootScope.GUI = LSM.Load('GUI') || $scope.GUIDefaults;
        $log.debug('Login GUI Loaded:', $rootScope.GUI);
        AuthForm.Submit = false;
        // Redirect to last visited route from localStorage or default route
        $location.path(LSM.Load('LastRoute') || '/jobs');
      },
      function(error) {
        AuthForm.Submit = false;
        error.status == 502 ? error.statusText = 'Main service is down (HTTP 502)' : null;
        Alerts.Add('auth', 'danger', error.statusText);
      }
    );
  };


  $scope.Logout = function() {
    Auth.Logout()
    .then(
      function(success) {
        // Redirect to login
        $location.path('/login');
      },
      function(error) {
        Alerts.Add('auth', 'danger', error.statusText);
      }
    );
  }

});
