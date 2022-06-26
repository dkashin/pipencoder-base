
app.controller('EventsController', function($rootScope, $scope, $log, $http, $interval, Alerts, Events) {

  var Polls = {
    Events: { Checker: null, Timer: 3000 }
  };

  $scope.ContentLoaded = false;
  $scope.Chapters = 'Events';


  $scope.SystemUpdateApply = function() {
    $scope.StopPolls();
    $rootScope.Stats.Update.Submit = true;
    $http.post('/api/v1/tools/update_apply')
    .then(
      function(success) {
        $log.debug('SystemUpdateApply response: ', success.data);
        Events.Minus(1);
        $scope.EventsCheck();
        $rootScope.Stats.Update.new_version = success.data.new_version;
        Alerts.Add('events', 'success', 'System Update: ' + success.statusText);
      },
      function(error) {
        $log.error('SystemUpdateApply response: ', error);
        Alerts.Add('events', 'danger', 'System Update: ' + error.statusText);
      })
    .finally(function() {
      $scope.StartPolls();
      $rootScope.Stats.Update.Submit = false;
    });
  }


  $scope.EventsCheck = function() {
    $scope.EventsCounter = Events.Get()
    $scope.ContentLoaded = true;
//    $rootScope.LicenseInfo ? $scope.ContentLoaded = true : null;
  }


  $scope.StartPolls = function() {
    $scope.StopPolls();
    Polls.Events.Checker = $interval(function() {
      if ($rootScope.CurrentUser.Name) {
        $scope.EventsCheck();
      }
    }, Polls.Events.Timer);
    $log.debug('Events poll started');
  }


  $scope.StopPolls = function() {
    $interval.cancel(Polls.Events.Checker);
    $log.debug('Events poll terminated!');
  }


  $scope.$on('$destroy', function() {
    $scope.StopPolls();
  });


  // First load controller init
  $scope.ControllerInit = function() {
    if ($rootScope.CurrentUser.Name) {
      // Init event checker
      $scope.EventsCheck();
    }
  }

  $scope.ControllerInit();
  $scope.StartPolls();

});
