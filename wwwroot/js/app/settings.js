
app.controller('SettingsController', function($rootScope, $scope, $location, $log, $http, Alerts, AVPresets, Tools, ServerList, Node) {

  $scope.ContentLoaded = false;
  $scope.Chapters = 'Settings';
  $scope.User = { Confirm: {} };
  $scope.Server = { List: {}, Action: { Edit: false } };

  // Supported encoder options
  $scope.AVPresets = [
    {
      Header: 'Video presets',
      Show: false, Confirm: false, Submit: false, Action: null, Type: 'video',
      Data: {},
      Codecs: {
        Model: 'vcodec', Default: 'libx264',
        Values: [
          { Value: 'libx264', Alias: 'libx264' },
          { Value: 'libx265', Alias: 'libx265' },
          { Value: 'h264_nvenc', Alias: 'h264_nvenc' },
          { Value: 'hevc_nvenc', Alias: 'hevc_nvenc' },
          { Value: 'v210', Alias: 'decklink' }
        ]
      },
      CodecOptions: [
        {
          Name: 'Preset', Model: 'vpreset', Type: 'select', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc',
          Values: [
            { Value: 'ultrafast', Alias: 'ultrafast', CodecList: 'libx264, libx265' },
            { Value: 'superfast', Alias: 'superfast', CodecList: 'libx264, libx265' },
            { Value: 'veryfast', Alias: 'veryfast', CodecList: 'libx264, libx265', Default: true },
            { Value: 'faster', Alias: 'faster', CodecList: 'libx264, libx265' },
            { Value: 'fast', Alias: 'fast', CodecList: 'libx264, libx265' },
            { Value: 'medium', Alias: 'medium', CodecList: 'libx264, libx265' },
            { Value: 'slow', Alias: 'slow', CodecList: 'libx264, libx265' },
            { Value: 'slower', Alias: 'slower', CodecList: 'libx264, libx265' },
            { Value: 'veryslow', Alias: 'veryslow', CodecList: 'libx264, libx265' },
            { Value: 'hp', Alias: 'high performance', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'hq', Alias: 'high quality', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'll', Alias: 'low latency', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'llhq', Alias: 'low latency hq', CodecList: 'h264_nvenc, hevc_nvenc', Default: true },
            { Value: 'llhp', Alias: 'low latency hp', CodecList: 'h264_nvenc, hevc_nvenc' }
          ]
        },
        {
          Name: 'Profile', Model: 'vprofile', Type: 'select', CodecList: 'libx264, h264_nvenc, hevc_nvenc',
          Values: [
            { Value: 'baseline', Alias: 'baseline', CodecList: 'libx264, h264_nvenc' },
            { Value: 'main', Alias: 'main', CodecList: 'ALL', Default: true },
            { Value: 'main10', Alias: 'main10', CodecList: 'hevc_nvenc' },
            { Value: 'high', Alias: 'high', CodecList: 'libx264, h264_nvenc' },
            { Value: 'high10', Alias: 'high10', CodecList: 'libx264' },
            { Value: 'high422', Alias: 'high422', CodecList: 'libx264' },
            { Value: 'high444', Alias: 'high444', CodecList: 'libx264' },
            { Value: 'high444p', Alias: 'high444p', CodecList: 'h264_nvenc' },
            { Value: 'rext', Alias: 'rext', CodecList: 'hevc_nvenc' }
          ]
        },
        {
          Name: 'Level', Model: 'level', Type: 'select', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc',
          Values: [
            { Value: null, Alias: 'Auto', CodecList: 'ALL', Default: true },
            { Value: '1', Alias: '1', CodecList: 'ALL' },
            { Value: '1b', Alias: '1b', CodecList: 'libx264, h264_nvenc' },
            { Value: '1.1', Alias: '1.1', CodecList: 'libx264, h264_nvenc' },
            { Value: '1.2', Alias: '1.2', CodecList: 'libx264, h264_nvenc' },
            { Value: '1.3', Alias: '1.3', CodecList: 'libx264, h264_nvenc' },
            { Value: '2', Alias: '2', CodecList: 'ALL' },
            { Value: '2.1', Alias: '2.1', CodecList: 'ALL' },
            { Value: '2.2', Alias: '2.2', CodecList: 'libx264, h264_nvenc' },
            { Value: '3', Alias: '3', CodecList: 'ALL' },
            { Value: '3.1', Alias: '3.1', CodecList: 'ALL' },
            { Value: '3.2', Alias: '3.2', CodecList: 'libx264, h264_nvenc' },
            { Value: '4', Alias: '4', CodecList: 'ALL' },
            { Value: '4.1', Alias: '4.1', CodecList: 'ALL' },
            { Value: '4.2', Alias: '4.2', CodecList: 'libx264, h264_nvenc' },
            { Value: '5', Alias: '5', CodecList: 'ALL' },
            { Value: '5.1', Alias: '5.1', CodecList: 'ALL' },
            { Value: '5.2', Alias: '5.2', CodecList: 'libx264, libx265, hevc_nvenc' },
            { Value: '6', Alias: '6', CodecList: 'libx264, libx265, hevc_nvenc' },
            { Value: '6.1', Alias: '6.1', CodecList: 'libx264, libx265, hevc_nvenc' },
            { Value: '6.2', Alias: '6.2', CodecList: 'libx264, libx265, hevc_nvenc' }
          ]
        },
        {
          Name: 'Subsample', Model: 'subsample', Type: 'select', CodecList: 'ALL',
          Values: [
            { Value: 'yuv420p', Alias: 'yuv420p', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Default: true },
            { Value: 'yuv422p', Alias: 'yuv422p', CodecList: 'libx264, libx265' },
            { Value: 'yuv444p', Alias: 'yuv444p', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc' },
            { Value: 'yuv444p16le', Alias: 'yuv444p16le', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'nv12', Alias: 'nv12', CodecList: 'libx264, h264_nvenc, hevc_nvenc' },
            { Value: 'nv16', Alias: 'nv16', CodecList: 'libx264' },
            { Value: 'nv21', Alias: 'nv21', CodecList: 'libx264' },
            { Value: 'p010le', Alias: 'p010le', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'rgb0', Alias: 'rgb0', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'nv12', Alias: 'nv12', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'cuda', Alias: 'cuda', CodecList: 'h264_nvenc, hevc_nvenc' },
            { Value: 'uyvy422', Alias: 'uyvy422', CodecList: 'v210', Default: true }
          ]
        },
        {
          Name: 'CBR Mode', Model: 'cbr', Type: 'select', CodecList: 'h264_nvenc, hevc_nvenc',
          Values: [
            { Value: true, Alias: 'Yes', CodecList: 'ALL' },
            { Value: false, Alias: 'No', CodecList: 'ALL', Default: true }
          ]
        },
        {
          Name: 'Spatial AQ', Model: 'spatial_aq', Type: 'select', CodecList: 'h264_nvenc, hevc_nvenc',
          Values: [
            { Value: true, Alias: 'Yes', CodecList: 'ALL' },
            { Value: false, Alias: 'No', CodecList: 'ALL', Default: true }
          ]
        },
        {
          Name: 'Temporal AQ', Model: 'temporal_aq', Type: 'select', CodecList: 'h264_nvenc, hevc_nvenc',
          Values: [
            { Value: true, Alias: 'Yes', CodecList: 'ALL' },
            { Value: false, Alias: 'No', CodecList: 'ALL', Default: true }
          ]
        },
        {
          Name: 'Strict GOP', Model: 'strict_gop', Type: 'select', CodecList: 'h264_nvenc, hevc_nvenc',
          Values: [
            { Value: true, Alias: 'Yes', CodecList: 'ALL', Default: true },
            { Value: false, Alias: 'No', CodecList: 'ALL' }
          ]
        },
        {
          Name: 'Zero latency', Model: 'zerolatency', Type: 'select', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc',
          Values: [
            { Value: true, Alias: 'On', CodecList: 'ALL' },
            { Value: false, Alias: 'Off', CodecList: 'ALL', Default: true }
          ]
        },
        {
          Name: 'RC Lookahead', Model: 'rc_lookahead', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'frames'
        },
        {
          Name: 'Rate control', Model: 'rc', Type: 'select', CodecList: 'h264_nvenc, hevc_nvenc',
          Values: [
            { Value: 'constqp', Alias: 'constqp', CodecList: 'ALL' },
            { Value: 'vbr', Alias: 'vbr', CodecList: 'ALL' },
            { Value: 'cbr', Alias: 'cbr', CodecList: 'ALL' },
            { Value: 'cbr_ld_hq', Alias: 'cbr_ld_hq', CodecList: 'ALL' },
            { Value: 'cbr_hq', Alias: 'cbr_hq', CodecList: 'ALL' },
            { Value: 'vbr_hq', Alias: 'vbr_hq', CodecList: 'ALL', Default: true }
          ]
        },
        {
          Name: 'Coder type', Model: 'coder', Type: 'select', CodecList: 'h264_nvenc',
          Values: [
            { Value: 'auto', Alias: 'auto', CodecList: 'ALL' },
            { Value: 'cabac', Alias: 'cabac', CodecList: 'ALL', Default: true },
            { Value: 'cavlc', Alias: 'cavlc', CodecList: 'ALL' },
            { Value: 'ac', Alias: 'ac', CodecList: 'ALL' },
            { Value: 'vlc', Alias: 'vlc', CodecList: 'ALL' }
          ]
        },
        {
          Name: 'Closed Captions', Model: 'cc_copy', Type: 'select', CodecList: 'libx264, h264_nvenc',
          Values: [
            { Value: true, Alias: 'Copy', CodecList: 'ALL', Default: true },
            { Value: false, Alias: 'Discard', CodecList: 'ALL' }
          ]
        },
        { Name: 'Bitrate', Model: 'vbitrate', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'kbps' },
        { Name: 'Buffer', Model: 'vbuffer', Type: 'input', CodecList: 'ALL', Info: 'kilobytes' },
        { Name: 'Minrate', Model: 'minrate', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'kilobytes' },
        { Name: 'Maxrate', Model: 'maxrate', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'kilobytes' },
        { Name: 'Frames/sec', Model: 'fps', Type: 'input', CodecList: 'ALL', Info: 'frames' },
        { Name: 'GOP Size', Model: 'gop', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'frames' },
        { Name: 'Keyframes min interval', Model: 'keyint_min', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'frames' },
        { Name: 'Keyframes every', Model: 'keyframes', Type: 'input', CodecList: 'libx264, libx265, h264_nvenc, hevc_nvenc', Info: 'second(s)' },
        { Name: 'Custom options', Model: 'vcustom', Type: 'input', CodecList: 'ALL', Info: 'extra tune' }
      ]
    },
    {
      Header: 'Audio presets',
      Show: false, Confirm: false, Submit: false, Action: null, Type: 'audio',
      Data: {},
      Codecs: {
        Model: 'acodec', Default: 'libfdk_aac',
        Values: [
          { Value: 'libfdk_aac', Alias: 'AAC' },
          { Value: 'libmp3lame', Alias: 'MP3' },
          { Value: 'pcm_s16le', Alias: 'decklink' }
        ]
      },
      CodecOptions: [
        { Name: 'Bitrate', Model: 'abitrate', Type: 'input', CodecList: 'libfdk_aac, libmp3lame', Info: 'kbps' },
        {
          Name: 'Rate (Hz)', Model: 'sample_rate', Type: 'select', CodecList: 'ALL',
          Values: [
            { Value: null, Alias: 'Original', CodecList: 'libfdk_aac, libmp3lame', Default: true },
            { Value: 8000, Alias: '8000', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 11025, Alias: '11025', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 22050, Alias: '22050', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 44100, Alias: '44100', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 48000, Alias: '48000', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 48000, Alias: '48000', CodecList: 'pcm_s16le', Default: true },
            { Value: 96000, Alias: '96000', CodecList: 'libfdk_aac, libmp3lame' }
          ]
        },
        {
          Name: 'Channels', Model: 'channels', Type: 'select', CodecList: 'ALL',
          Values: [
            { Value: null, Alias: 'Original', CodecList: 'libfdk_aac, libmp3lame', Default: true },
            { Value: 1, Alias: '1', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 2, Alias: '2', CodecList: 'libfdk_aac, libmp3lame' },
            { Value: 2, Alias: '2', CodecList: 'pcm_s16le', Default: true },
            { Value: 4, Alias: '4', CodecList: 'pcm_s16le' },
            { Value: 8, Alias: '8', CodecList: 'pcm_s16le' },
            { Value: 16, Alias: '16', CodecList: 'pcm_s16le' }
          ]
        },
        { Name: 'Custom options', Model: 'acustom', Type: 'input', CodecList: 'ALL', Info: 'extra tune' }
      ]
    }
  ];
  $scope.Failover = {
    Types: [ 'Clip', 'Image', 'URL' ],
    Media: { Type: 'URL', URL: null, Image: null, Clip: null },
    PIDMap: [
      { Type: 'Video', dbName: 'default_fail_vpid' },
      { Type: 'Audio', dbName: 'default_fail_apid' },
      { Type: 'Data', dbName: 'default_fail_dpid' }
    ],
    VideoDecoders: [ 'libavcodec', 'mpeg2_cuvid', 'h264_cuvid' ],
    DecoderErrDetect: [ 'crccheck', 'bitstream', 'buffer', 'explode', 'ignore_err', 'careful', 'compliant', 'aggressive' ],
  //  UDPShow: false,
  //  HTTPShow: false,
  //  MPEGTSShow: false
  }
  $scope.AlarmPeriodList = [
    { 'value': 60, 'alias': 'Minute' },
    { 'value': 3600, 'alias': 'Hour' },
    { 'value': 86400, 'alias': 'Day' }
  ];
  $scope.Settings = {};
  //$scope.user_form_data = {};
  $scope.server_form_data = {};
  $scope.Node = { Data: {}, Submit: false };


  String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  }


  String.prototype.uncapitalize = function() {
    return this.charAt(0).toLowerCase() + this.slice(1);
  }


  // Node service
  $scope.NodeService = function(API) {
    $scope.Node.Submit = true;
    $log.debug('NodeService request: ', $scope.Node.Data);
    Node.Service(API, $scope.Node.Data)
    .then(
      function(success) {
//        API == 'auth' ? $scope.Settings.account_email = $scope.Node.Data.account_email : null;
//        API == 'deactivate' ? $scope.Settings.account_email = null : null;
        Alerts.Add('settings', 'success', 'License ' + API + ': ' + success.statusText);
      },
      function(error) {
        Alerts.Add('settings', 'danger', 'License ' + API + ': ' + error.statusText);
      }
    )
    .finally(function() {
      $scope.Node.Submit = false;
    });
  }


  function StringContains(target, pattern){
    var value = 0;
    pattern.forEach(function(word) {
      value = value + target.includes(word);
    });
    return (value === 1);
  }


  // Show source extra options
  $scope.FailoverSelect = function(Failover) {
    Failover.UDPShow = false;
    Failover.HTTPShow = false;
    Failover.MPEGTSShow = false;
    var FailoverMediaType = Failover.Media.Type;
    var FailoverMedia = Failover.Media[FailoverMediaType];
    if (FailoverMedia) {
      if (StringContains(FailoverMedia, [ 'udp://', 'srt://' ])) {
        Failover.UDPShow = true;
      }
      if (StringContains(FailoverMedia, [ 'http://', 'https://' ])) {
        Failover.HTTPShow = true;
      }
      if (StringContains(FailoverMedia, [ 'udp://', 'srt://', '.ts', '.mpeg', '.mpg' ])) {
        Failover.MPEGTSShow = true;
      }
    }
    $scope.Settings.default_fail_type = FailoverMediaType;
    $scope.Settings.default_fail_src = FailoverMedia;
    $log.debug('FailoverSelect: Failover: ', Failover);
  }


  // Get settings
  $scope.GetSettings = function() {
    $http.post('/api/v1/settings/load')
    .then(
      function(success) {
        $log.debug('GetSettings response:', success);
        var data = success.data;
        $scope.Settings = data.settings;
        $scope.MediaAssets = data.media;
        $scope.Failover.Media.Image = data.media.images[0];
        $scope.Failover.Media.Clip = data.media.clips[0];
        $scope.Failover.Media.URL = null;
        $scope.Failover.Media.Type = $scope.Settings.default_fail_type;
        $scope.Failover.Media[$scope.Failover.Media.Type] = $scope.Settings.default_fail_src;
        $scope.Settings.default_fail_decoder ? null : $scope.Failover.VideoDecoders[0];
        $scope.Settings.default_fail_decoder_err_detect ? null : $scope.Failover.DecoderErrDetect[0];
        $scope.FailoverSelect($scope.Failover);
      },
      function(error) {
        $log.error('GetSettings response:', error);
        Alerts.Add('settings', 'danger', 'Load settings: ' + error.statusText);
      }
    )
    .finally(function() {
      $scope.ContentLoaded = true;
    });
  }


  // Save settings
  $scope.SaveSettings = function(action) {
    if (!$scope.Settings.alarm_master_email) { $scope.Settings.alarm_master = false; }
    if (!$scope.Settings.alarm_error_email && !$scope.Settings.alarm_master_email) { $scope.Settings.alarm_error = false; }
    if (!$scope.Settings.alarm_action_email && !$scope.Settings.alarm_master_email) { $scope.Settings.alarm_action = false; }
    $log.debug('SaveSettings: Settings: ', $scope.Settings);
    $http.post('/api/v1/settings/save', $scope.Settings)
    .then(
      function(success) {
        $log.debug('SaveSettings response: ', success);
        Alerts.Add('settings', 'success', 'Save settings: ' + success.statusText);
      },
      function(error) {
        $log.error('SaveSettings response: ', error);
        Alerts.Add('settings', 'danger', 'Save settings: ' + error.statusText);
      }
    );
  }


  // Get users list
  $scope.GetUsersList = function() {
    $scope.User.Header = 'Users list';
    $http.post('/api/v1/user/list')
    .then(
      function(success) {
        $log.debug('GetUsersList response: ', success);
        var data = success.data;
        $scope.UsersList = data.users;
        $scope.User.Selected = data.users[0];
        $log.debug('GetUsersList: UsersList ', $scope.UsersList);
      },
      function(error) {
        $log.error('GetUsersList response:', error);
        Alerts.Add('settings', 'danger', 'Load users: ' + error.statusText);
      }
    );
  }


  // User action panel
  $scope.UserAction = function(action) {
    $scope.User.Show = !$scope.User.Show;
    $scope.User.Action = action;
    $scope.User.PasswordMsg = null;
    if (action == 'add') {
      $scope.User.Header = 'Add User';
      $scope.User.Selected = {};
    }
    if (action == 'edit') {
      $scope.User.PasswordMsg = 'empty for keep existing';
      $scope.User.Header = 'Edit User';
      //$scope.user_form_data = angular.copy($scope.User.Selected);
    }
    if (action == 'cancel') {
      //$scope.user_form_data = {};
      $scope.GetUsersList();
      $scope.User.Confirm.Submit = false;
    }
  }


  // User manage
  $scope.UserManage = function(action) {
    $scope.User.Confirm.Submit = true;
    if (action == 'add') {
      $log.debug('UserManage Add: User.Selected: ', $scope.User.Selected);
      $http.post('/api/v1/user/add', $scope.User.Selected)
      .then(
        function(success) {
          $log.debug('UserManage Add response: ', success);
          Alerts.Add('settings', 'success', 'Add user: ' + success.statusText);
        },
        function(error) {
          $log.error('UserManage Add response: ', error);
          Alerts.Add('settings', 'danger', 'Add user: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.UserAction('cancel');
      });
    }
    if (action == 'edit') {
      $log.debug('UserManage Edit: User.Selected: ', $scope.User.Selected);
      $http.post('/api/v1/user/update', $scope.User.Selected)
      .then(
        function(success) {
          $log.debug('UserManage Edit response: ', success);
          Alerts.Add('settings', 'success', 'Update user: ' + success.statusText);
        },
        function(error) {
          $log.error('UserManage Edit response: ', error);
          Alerts.Add('settings', 'danger', 'Update user: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.UserAction('cancel');
      });
    }
    if (action == 'delete') {
      $log.debug('UserManage Delete: User ID: ', $scope.User.Selected.id);
      if ($rootScope.CurrentUser.Name == $scope.User.Selected.username) {
        $location.path('/login');
      }
      $http.post('/api/v1/user/delete', { id: $scope.User.Selected.id })
      .then(
        function(success) {
          $log.debug('UserManage Delete response: ', success);
          Alerts.Add('settings', 'success', 'Delete user: ' + success.statusText);
        },
        function(error) {
          $log.error('UserManage Delete response: ', error);
          Alerts.Add('settings', 'danger', 'Delete user: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.GetUsersList();
        $scope.User.Confirm.Delete = false;
        $scope.User.Confirm.Submit = false;
      });
    }
  }


  // Server list request
  $scope.ServerListGet = function() {
    $scope.Server.Header = 'Servers list';
    ServerList.Get($scope.Server)
    .then(
      function(servers) {
        $scope.Server.List = servers.List;
        $scope.Server.Selected = servers.List[0];
        $log.debug('ServerListGet: Server: ', $scope.Server);
      },
      function(error) {
        Alerts.Add('settings', 'danger', 'ServerList: ' + error.statusText);
      }
    );
  }


  // Server action panel
  $scope.ServerAction = function(action) {
    $scope.SelectedServerAction = action;
    $scope.ServerFeatures = {};
    if (action == 'add') {
      $scope.server_form_data = { hls_srv: null, rtmp_srv: null };
      $scope.Server.Header = 'Add Server';
      $scope.Server.Action.Edit = true;
    }
    if (action == 'edit') {
      $log.debug('ServerAction: Server.Selected: ', $scope.Server.Selected);
      $scope.Server.Header = 'Edit Server';
      $scope.Server.Action.Edit = true;
      $scope.server_form_data = angular.copy($scope.Server.Selected);
      $scope.server_form_data.hls_srv = null;
      $scope.server_form_data.rtmp_srv = null;
      for (f in $scope.server_form_data.features) {
        var feature = $scope.server_form_data.features[f];
        $scope.ServerFeatures[feature.name] = true;
        if (feature.name == 'HLS') { $scope.server_form_data.hls_srv = feature.url; }
        if (feature.name == 'RTMP') { $scope.server_form_data.rtmp_srv = feature.url; }
      }
      var jobs_restart = false;
      var exceptions = [ 'name' ];
      $scope.server_form_data_copy = angular.copy($scope.server_form_data);
      $scope.server_form_data.jobs_restart = Tools.CompareObj(jobs_restart, $scope.server_form_data_copy, $scope.server_form_data, exceptions);
    }
    if (action == 'delete') {
      $scope.Server.Action.Delete = true;
      $scope.Server.Header = 'Delete Server';
    }
    if (action == 'cancel') {
      $scope.ServerListGet();
      $scope.Server.Action.Delete = false;
      $scope.Server.Action.Edit = false;
    }
  }


  // Server main IP mapping to URL(s)
  $scope.ServerIPMapping = function(ip) {
    if ($scope.ServerFeatures.HLS) { $scope.server_form_data.hls_srv = 'http://' + ip };
    if ($scope.ServerFeatures.RTMP) { $scope.server_form_data.rtmp_srv = 'rtmp://' + ip };
  }


  // Server submit manager
  $scope.ServerManage = function(action) {
    $scope.Server.Action.Submit = true;
    $log.debug('ServerManage Add data:', $scope.server_form_data);
    if (action == 'add') {
      $http.post('/api/v1/server/add', $scope.server_form_data)
      .then(
        function(success) {
          $log.debug('ServerManage Add response:', success);
          Alerts.Add('settings', 'success', 'Add server: ' + success.statusText);
        },
        function(error) {
          $log.error('ServerManage Add response:', error);
          Alerts.Add('settings', 'danger', 'Add server: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.ServerAction('cancel');
        $scope.Server.Action.Submit = false;
      });
    }
    if (action == 'edit') {
      $log.debug('ServerManage Update data:', $scope.server_form_data);
      $http.post('/api/v1/server/update', $scope.server_form_data)
      .then(
        function(success) {
          $log.debug('ServerManage Update response: ', success);
          Alerts.Add('settings', 'success', 'Update server: ' + success.statusText);
        },
        function(error) {
          $log.error('ServerManage Update response: ', error);
          Alerts.Add('settings', 'danger', 'Update server: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.ServerAction('cancel');
        $scope.Server.Action.Submit = false;
      });
    }
    if (action == 'delete') {
      $scope.Server.Action.Delete = false;
      $log.debug('ServerManage Delete: Server.Selected.id: ', $scope.Server.Selected.id);
      $http.post('/api/v1/server/delete', { 'id': $scope.Server.Selected.id })
      .then(
        function(success) {
          $log.debug('ServerManage Delete response: ', success);
          Alerts.Add('settings', 'success', 'Delete server: ' + success.statusText);
          $scope.ServerListGet();
        },
        function(error) {
          $log.error('ServerManage Delete response: ', error);
          Alerts.Add('settings', 'danger', 'Delete server: ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.ServerAction('cancel');
        $scope.Server.Action.Submit = false;
      });
    }
  }


  // Restart app core
  $scope.AppRestart = function() {
    $http.post('/api/v1/tools/app_restart')
    .then(
      function(success) {
        $log.debug('AppRestart response: ', success);
        Alerts.Add('settings', 'success', 'App restart: ' + success.statusText);
      },
      function(error) {
        $log.error('AppRestart response: ', error);
        Alerts.Add('settings', 'danger', 'App restart: ' + error.statusText);
      }
    );
  }


  // Reboot server
  $scope.ServerReboot = function() {
    $http.post('/api/v1/tools/system_reboot')
    .then(
      function(success) {
        $log.debug('ServerReboot response: ', success);
        $scope.ContentLoaded = false;
        Alerts.Add('settings', 'success', 'Reboot: ' + success.statusText);
      },
      function(error) {
        $log.error('ServerReboot response: ', error);
        Alerts.Add('settings', 'danger', 'Reboot: ' + error.statusText);
      }
    )
    .finally(function() {
      $scope.RebootConfirm = false;
    });
  }


  // Get AV presets list
  $scope.GetPresetsList = function() {
    AVPresets.Get()
    .then(
      function(PresetData) {
        for (Preset in $scope.AVPresets) {
          $scope.AVPresets[Preset].List = PresetData[$scope.AVPresets[Preset].Type];
          $scope.AVPresets[Preset].Data = $scope.AVPresets[Preset].List[0];
        }
      },
      function(error) {
        Alerts.Add('settings', 'danger', 'AV Presets: ' + error.statusText);
      }
    );
  }


  // Show only selected presets
  $scope.PresetHide = function(condition) {
    return function(preset) {
      if (preset.filename != condition) { return true; } else { return false; }
    };
  }


  $scope.PresetCodecChange = function(Preset, CodecSelected) {
    Preset.Data = {};
    Preset.Data[Preset.Codecs.Model] = CodecSelected;
    for (Option in Preset.CodecOptions) {
      Option = Preset.CodecOptions[Option];
      if ($scope.PresetOptionsShow(Option.CodecList, CodecSelected) && Option.Type == 'select') {
        for (Value in Option.Values) {
          OptionValue = Option.Values[Value];
          if ($scope.PresetOptionsShow(OptionValue.CodecList, CodecSelected) && OptionValue.Default) {
            Preset.Data[Option.Model] = OptionValue.Value;
          }
        }
      } else {
        delete Preset.Data[Option.Model];
      }
    }
    $log.debug('PresetCodecChange: Preset: ', Preset);
  }


  $scope.PresetOptionsShow = function(CodecList, CodecSelected) {
    return ((CodecList.indexOf(CodecSelected) > -1) || (CodecList == 'ALL')) ? true : false;
  }


  $scope.PresetOptionsFilter = function(CodecSelected) {
    return function(Option) {
      return ((Option.CodecList.indexOf(CodecSelected) > -1) || (Option.CodecList == 'ALL')) ? true : false;
    };
  }


  // Preset manager
  $scope.PresetManager = function(SelectedPreset, PresetAction) {
    SelectedPreset.Action = PresetAction;
    SelectedPreset.Header = PresetAction + ' preset';
    if (PresetAction == 'Add') {
      // Initialize preset with default values
      $scope.PresetCodecChange(SelectedPreset, SelectedPreset.Codecs.Default);
      SelectedPreset.Show = !SelectedPreset.Show;
    }
    if (PresetAction == 'Update') {
      if (SelectedPreset.Type == 'audio') {
        if (!SelectedPreset.Data.sample_rate) { SelectedPreset.Data.sample_rate = null; }
        if (!SelectedPreset.Data.channels) { SelectedPreset.Data.channels = null; }
      }
      if (SelectedPreset.Type == 'video') {
        if (!SelectedPreset.Data.level) { SelectedPreset.Data.level = null; }
      }
      SelectedPreset.Show = !SelectedPreset.Show;
    }
    if (PresetAction == 'Delete') {
      SelectedPreset.Confirm = true;
    }
    $log.debug('PresetManager: SelectedPreset: ', SelectedPreset);
  }


  // Preset submit data
  $scope.PresetSubmit = function(SelectedPreset, PresetAction) {
    SelectedPreset.Submit = true;
    var PresetDataJSON = {
      'preset_name': SelectedPreset.Data.filename,
      'preset_type': SelectedPreset.Type
    }
    delete SelectedPreset.Data.filename;
    for (SPD in SelectedPreset.Data) {
      if (SelectedPreset.Data[SPD] == null) { delete SelectedPreset.Data[SPD]; }
    }
    PresetDataJSON.preset_data = SelectedPreset.Data;
    $log.debug('PresetSubmit ', PresetAction, ': PresetDataJSON: ', PresetDataJSON);
    $http.post('/api/v1/preset/' + PresetAction.uncapitalize(), PresetDataJSON)
    .then(
      function(success) {
        $log.debug('PresetSubmit', PresetAction, 'response:', success);
        $scope.PresetCancel(SelectedPreset);
        if (PresetAction == 'Delete') { SelectedPreset.Confirm = false; }
        Alerts.Add('settings', 'success', PresetAction + ' preset: ' + success.statusText);
      },
      function(error) {
        $log.error('PresetSubmit', PresetAction, 'response:', error);
        Alerts.Add('settings', 'danger', PresetAction + ' preset: ' + error.statusText);
      }
    )
    .finally(function() {
      SelectedPreset.Submit = false;
    });
  }


  // Preset cancel
  $scope.PresetCancel = function(SelectedPreset) {
    SelectedPreset.Header = SelectedPreset.Type.capitalize() + ' presets';
    SelectedPreset.Show = false;
    SelectedPreset.Confirm = false;
    SelectedPreset.Action = null;
    $scope.GetPresetsList();
  }


  // First load controller init
  $scope.ControllerInit = function() {
    if ($rootScope.CurrentUser) {
      if ($rootScope.CurrentUser.isAdmin) {
        // Request user list
        $scope.GetUsersList();
        // Request AV presets list
        $scope.GetPresetsList();
        // Request server list
        $scope.ServerListGet();
        // Request app settings
        $scope.GetSettings();
      }
    }
  }

  $scope.ControllerInit();

});
