
app.controller('NavController', function($rootScope, $scope, $log, $http, $location, $interval, AppUpdate, Events, Stats, LSM) {

  var Polls = {
    System: { Checker: null, Timer: 2000 },
    Update: { Checker: null, Timer: 60000 }
  };


  $scope.SideNavActive = function(page) {
    var currentRoute = $location.path().substring(1) || 'jobs';
    return page === currentRoute ? 'active' : '';
  }


  // Server stats collapse
  $scope.ServerStatShow = function() {
    $rootScope.GUI.Navbar.StatCollapse = !$rootScope.GUI.Navbar.StatCollapse
    LSM.Save({ GUI: $rootScope.GUI });
  }


  // GPU stats selected
  $scope.SelectGPU = function(StatGPUSelected) {
    LSM.Save({ GUI: $rootScope.GUI });
  }


  $scope.UpdateCheck = function() {
    AppUpdate.Check().then(function(data) {}, function(error) {});
  }


  $scope.StatsGet = function() {
    Stats.Get()
    .then(
      function(success) {
        var hardware = angular.copy(success.data.hardware);
        //$log.debug(hardware);
        Object.keys(hardware).forEach(function(device_name) {
          var device_data = hardware[device_name];
          if (device_name == 'gpu') {
            var gpu_data = device_data.dev_data;
            var gpu_counter = device_data.dev_count;
            if (gpu_counter && gpu_data) {
              gpu_data.forEach(function(gpu) {
                if (gpu_counter > 1 && gpu.idx > 0) {
                  gpu.dev_name += ' (' + (gpu.idx - 1).toString() + ')';
                }
                if (!gpu.active) {
                  Object.keys(gpu.dev_opt).forEach(function(dev_opt) {
                    gpu.dev_opt[dev_opt] = 101;
                  });
                }
              });
            };
          } else {
            if (!device_data && device_data != 0) { device_data = 101; };
          };
        });
        $rootScope.Stats.Hardware = hardware;
        $log.debug('Stats hardware:', $rootScope.Stats.Hardware);
        // GPU stats only
        $rootScope.Stats.GPUData = hardware.gpu.dev_data;
      },
      function(error) {}
    );
  }


  // Stat bar color mapping
  $scope.StatsColor = function(value) {
    var color = 'off';
    if (value >= 0 && value <= 60) { color = 'success'; } else
    if (value > 60 && value <= 85) { color = 'warning'; } else
    if (value > 85 && value <= 100) { color = 'danger'; }
    return color;
  }


  // Start poll(s)
  $scope.StartPolls = function() {
    $scope.StopPolls();
      // System info check
      Polls.System.Checker = $interval(function() {
        if ($rootScope.CurrentUser) {
          $scope.StatsGet();
          $scope.EventsCounter = Events.Get();
        }
      }, Polls.System.Timer);

      // System update check
      Polls.Update.Checker = $interval(function() {
        if ($rootScope.CurrentUser.Name) {
          $scope.UpdateCheck();
          $scope.EventsCounter = Events.Get();
        }
      }, Polls.Update.Timer);

      $log.debug('Navbar poll started');
  }


  // Stop poll(s)
  $scope.StopPolls = function() {
    $interval.cancel(Polls.System.Checker);
    $interval.cancel(Polls.Update.Checker);
    $log.debug('Navbar poll terminated');
  }

  // Stop main poll on "ng-view" change
  $scope.$on('$destroy', function() {
    $scope.StopPolls();
  });


  // First load controller init
  $scope.ControllerInit = function() {
    if ($rootScope.CurrentUser.Name) {
      // System stats get
      $scope.StatsGet();
      // System update check
      $scope.UpdateCheck();
      // Get events counter
      $scope.EventsCounter = Events.Get();
    }
  }

  $scope.ControllerInit();
  $scope.StartPolls();

});
