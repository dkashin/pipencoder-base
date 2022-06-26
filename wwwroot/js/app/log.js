

app.directive('showTail', function($timeout) {
  return {
    restrict: 'A',
    scope: { showTail: "=" },
    link: function(scope, element, attrs) {
      scope.$watchCollection('showTail',
        function(newVal) {
          $timeout(function() {
            element[0].scrollTop = element[0].scrollHeight;
          });
        }
      );
    }
  }
});


app.directive('whenScrolled', function() {
  return function(scope, element, attrs) {
    var raw = element[0];
      element.bind('scroll', function() {
// Scroll down
//        if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
// Scroll up
        if (raw.scrollTop <= 0) {
          element[0].scrollTop += 20;
          scope.$apply(attrs.whenScrolled);
        }
      });
  };
});


app.controller('LogController', function($rootScope, $scope, $interval, $log, $http, $uibModalInstance, JobData, Tools) {

// Poll for auto-reload requested data
var AutoReloadPoll;
// Job data
$scope.JobData = JobData.job_data;
// Job index
$scope.JobID = JobData.job_data.id;
// Job name
$scope.JobName = JobData.job_data.job_name;
// Content show init
$scope.Content = { Data: [], Events: 100, Offset: 0, AutoReload: false, Type: 'log' };
// Init log scroll to the bottom
$scope.isScrolledBottom = false;
// Log files list
$scope.LogList = [
  { 'alias': 'Encoder log', 'log_dir': 'jobs', 'log_name': 'encoder' },
  { 'alias': 'Check log', 'log_dir': 'jobs', 'log_name': 'check' },
  { 'alias': 'Job log', 'log_dir': 'jobs', 'log_name': 'job' }
];
// Manifests links list
$scope.HLSManifestList = Tools.PreviewURL(JobData, 'list', 'static', null, 'HLS');


// Get log content from server
$scope.GetLog = function() {
  if (!$scope.LogScroll) {
    var LogRequestData = {
      'log_dir': $scope.Content.Selected.log_dir,
      'log_name': $scope.JobID + '_' + $scope.Content.Selected.log_name + '.log',
      'read_from': 'end',
      'show_lines': $scope.Content.Events,
      'offset': $scope.Content.Offset
    };
    $log.debug('Log: LogRequestData: ', LogRequestData);
    $scope.LogScroll = true;
    $http.post('/api/v1/tools/get_log', LogRequestData)
    .then(
      function(success) {
        var data = success.data;
        var content_data = data.content || '';
        $log.debug('GetLog response:', success);
        if ($scope.Content.AutoReload || $scope.Content.Offset == 0) {
          $scope.Content.Data = content_data;
        } else {
          $scope.Content.Data = content_data.concat($scope.Content.Data);
        }
        $scope.Content.Offset += $scope.Content.Events;
      },
      function(error) {
        $log.error('GetLog response:', error);
        $scope.Content.Data = 'Log request error';
      })
    .finally(function() {
      $scope.LogScroll = false;
      $scope.isScrolledBottom = true;
    });
  }
}


// Get manifest content from URL
$scope.GetManifest = function() {
  if (!$scope.LogScroll) {
    $scope.LogScroll = true;
    $http.get($scope.Content.Selected.url)
    .then(
      function(success) {
        var data = success.data;
        $log.debug('GetManifest response: ', data);
        if (data) {
          if ($scope.Content.AutoReload || $scope.Content.Offset == 0) {
            $scope.Content.Data = data;
          } else {
            $scope.Content.Data = data.concat($scope.Content.Data);
          }
        } else {
          $scope.Content.Data = 'Manifest has no data';
        }
      },
      function(error) {
        $log.debug('GetManifest response: ', error);
        $scope.Content.Data = 'Manifest request error';
      })
    .finally(function() {
      $scope.LogScroll = false;
      $scope.isScrolledBottom = true;
    });
  }
}


// Reload content from server
$scope.ContentReload = function() {
  $scope.isScrolledBottom = false;
  $scope.Content.Offset = 0;
  if ($scope.Content.Type == 'log') {
    $scope.GetLog();
  }
  if ($scope.Content.Type == 'manifest') {
    $scope.GetManifest();
  }
}


// Set content type based on tab selected
$scope.ContentTypeSelector = function(type) {
  $scope.Content.Type = type;
  if ($scope.Content.Type == 'log') {
    $scope.Content.List = $scope.LogList;
  }
  if ($scope.Content.Type == 'manifest') {
    $scope.Content.List = $scope.HLSManifestList;
  }
  $scope.Content.Selected = $scope.Content.List[0];
  $scope.ContentReload();
  $log.debug('ContentTypeSelector: Content.Type: ', $scope.Content.Type, ', Content.List: ', $scope.Content.List);
}


$scope.AutoReloadCheck = function() {
  $scope.Content.AutoReload = !$scope.Content.AutoReload;
  $scope.Content.AutoReload ? $scope.AutoReloadStart() : $scope.AutoReloadStop();
}


// Start auto refresh
$scope.AutoReloadStart = function() {
  $scope.AutoReloadStop();
  AutoReloadPoll = $interval(function() {
    if ($rootScope.CurrentUser) {
      $scope.ContentReload();
    }
  }, 1000);
}


// Stop auto refresh
$scope.AutoReloadStop = function() {
  $interval.cancel(AutoReloadPoll);
}


// Closes the window
$scope.ModalClose = function() {
  $uibModalInstance.dismiss('cancel');
}


// Destroy all $interval polls
$scope.$on('$destroy', function() { $scope.AutoReloadStop(); });


// Main init

// Select initial content type
$scope.ContentTypeSelector('log');
$scope.ContentReload();

});
