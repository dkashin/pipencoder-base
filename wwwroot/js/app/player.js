
app.directive('vjsplayer', function() {
  return {
    template: '<video controls class="video-js vjs-default-skin embed-responsive-item" id="thePlayer" width="640" height="480"></video>'
  };
});

app.controller('PlayerController', function($log, $scope, $http, $uibModalInstance, JobData, Tools) {


$scope.ShowPlayer = false;
$scope.tooltipIsOpen = false;


function GetDRMTagValue(text) {
  var DRMTagValue = null;
  var allLines = text.split('\n');
  for (var i = 0; i < allLines.length; i++) {
    if (allLines[i].match('EXT-X-KEY')) {
      LineContent = allLines[i];
      var allLineTags = LineContent.split(',');
      var DRMTagKey = allLineTags[0].split('=');
      DRMTagValue = DRMTagKey[1];
      break;
    }
  }
  return DRMTagValue;
}


// Get manifest content from URL
$scope.GetManifest = function(manifest) {
  $http.get(manifest).then(
    function(success) {
      var data = success.data;
      //$log.debug('JobPreview: GetManifest response: ', data);
      if (data) {
        $scope.DRMTagValue = GetDRMTagValue(data);
      }
      $log.debug('JobPreview: GetManifest: DRM ', $scope.DRMTagValue);
    },
    function(error) {
      $log.error('JobPreview: GetManifest error: ', error);
    });
}


$scope.PlaySourceSelect = function(Media) {
  if (Media) {
    $scope.ShowPlayer = $scope.CheckURLPlayable($scope.SelectedURL);
    $log.debug('JobPreview: ShowPlayer ', $scope.ShowPlayer);
    if ($scope.ShowPlayer) {
      $log.debug('JobPreview: PlaySourceSelect: Media ', Media);
      var MIME;
      if (Media.stream_type == 'RTMP') { MIME = 'rtmp/mp4'; }
      if (Media.stream_type == 'HLS') {
        MIME = 'application/x-mpegurl';
        $scope.GetManifest(Media.url);
      }
      $log.debug('JobPreview: VJSPlayer ', $scope.VJSPlayer);
      $scope.VJSPlayer ? null : $scope.VJSPlayer = videojs('thePlayer');
      $scope.VJSPlayer.src({ type: MIME, src: Media.url });
      $scope.VJSPlayer.load();
      $scope.VJSPlayer.play();
      if (MIME == 'rtmp/mp4') {
        $scope.VJSPlayer.on('pause', function () {
          $scope.VJSPlayer.on('play', function () {
            $scope.VJSPlayer.load();
            $scope.VJSPlayer.play();
            //$scope.VJSPlayer.off('play');
          });
        });
      }
    } else { $scope.VJSPlayer ? $scope.VJSPlayer.reset() : null }
  } else { $scope.VJSPlayer ? $scope.VJSPlayer.reset() : null }
}


$scope.ModalClose = function() {
  $uibModalInstance.dismiss('cancel');
}


$scope.CheckURLPlayable = function(URL) {
  return (URL.stream_type == 'RTMP' || URL.stream_type == 'HLS') ? true : false;
}


$uibModalInstance.rendered.then(function() {
  // Get previews URL(s)
  $scope.PreviewURL = Tools.PreviewURL(JobData, 'list', 'static');
  $log.debug('JobPreview: PreviewURL: ', $scope.PreviewURL);
  if ($scope.PreviewURL) {
    // Select fisrt preview URL from the list
    $scope.SelectedURL = $scope.PreviewURL[0];
    $log.debug('JobPreview: SelectedURL ', $scope.SelectedURL);
    $scope.PlaySourceSelect($scope.SelectedURL);
  }
});


$uibModalInstance.result
  .then(function() {}, function() { $uibModalInstance.close(); })
  .finally(function() { $scope.VJSPlayer ? $scope.VJSPlayer.dispose() : null; });
});

