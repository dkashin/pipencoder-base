

var app = angular.module('MainApp', [ 'ngRoute', 'ui.bootstrap', 'ngclipboard' ]);


app.run(function ($rootScope, $log, $location, LSM) {

  // Handle route change
  $rootScope.$on('$routeChangeStart', function (event, next) {
    if ($rootScope.CurrentUser) {
      if (!next.$$route.originalPath.includes('login')) {
        // Save last visited route to localStorage
        LSM.Save({ LastRoute: next.$$route.originalPath });
      };
    };
  });

});


app.controller('AppController', function ($log, $rootScope, $scope, Auth, Alerts, Filters, LSM, Node) {

  // GUI defaults
  $scope.GUIDefaults = {
    Navbar: {
      StatGPUSelected: 0,
      StatCollapse: false
    },
    Jobs: {
      Layout: {
        Mode: 'List',
        List: { Grid: [ 3, 1 ], Index: 0, IndexMax: 1, IndexPrev: 0 },
        Monitor: { Grid: [ 12, 6, 4, 3, 2 ], Index: 2, IndexMax: 4, IndexPrev: 0 }
      },
      Filters: {
        Default: { field: 'sid', value: null, type: 'or' },
//        Active: [ { field: 'sid', value: null, type: 'or' } ],
        List: [ { field: 'sid', value: null, type: 'or' } ],
        Quick: { 'OK': false, 'ERR': false, 'UPD': false, 'OFF': false },
        Show: false
      },
      SortBy: 'sid',
      SortByOrder: 'asc',
      PerPage: 12,
      ActPage: 1
    }
  };

  // Global app alerts
  $scope.AF = Alerts;
  // Global app statistics
  $rootScope.Stats = { Update: {} };
  // License info
  $rootScope.LicenseInfo = null;

  $rootScope.CurrentUser = {};

  // TODO: Use factory filters
  //$scope.FF = Filters;
  //$scope.FF.Init($rootScope.GUI.Filters);

  // App init for logged user
  Auth.GetLoggedUser()
  .then(
    function(success) {
      // Check node activation
      Node.Service('activate').then(function(success) {}, function(error) {});
      // Load GUI from localStogare.<username> or GUI defaults
      $rootScope.GUI = LSM.Load('GUI') || $scope.GUIDefaults;
      $log.debug('AppController GUI loaded:', $rootScope.GUI);
    },
    function(error) {
      // handle 401, redirect to login form
    }
  );

});
