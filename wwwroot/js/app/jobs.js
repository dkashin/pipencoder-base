
app.controller('JobsController', function($rootScope, $scope, $log, $http, $interval, $window, $uibModal, Alerts, Tools, AVPresets, LSM, ServerList, Stats) {

  /// Variables init ///

  $scope.ToolsFactory = Tools;
  // GUI content ready trigger
  $scope.ContentLoaded = false;
  // Polls settings
  var Polls = {
    JobList: { Checker: null, Timer: 1000 }
  };
  // Jobs data
  $scope.Jobs = { List: [], Hash: null, Total: 0 };
  // Servers data
  $scope.Servers = { List: {}, Hash: null };
  // Job list action triggers
  $scope.Actions = { JobDelete: {}, JobBusy: {} };
  // Navbar titles
  $scope.ChapterTitle = 'Jobs';
  // DRM protection type
  $scope.DRMTypes = [ 'AES-128' ];
  // DRM data storage
  $scope.DRMStorages = [ 'Local', 'Remote' ];
  // Source types selection
  $scope.SourceTypes = [ 'Default', 'URL', 'Device', 'Clip', 'Image' ];
  // Target types selection
  $scope.TargetTypes = [ 'Stream', 'Device' ];
  // GPU list
  $scope.GPUList = [];
  // Video decoders
  $scope.Decklink = [
    { alias: 'Capture format', ff_opt: 'format_code', type: 'select', values: [] },
    { alias: 'Video input', ff_opt: 'video_input', type: 'select', values: [ 'sdi', 'hdmi', 'optical_sdi', 'component', 'composite', 's_video', 'unset' ] },
    { alias: 'Audio input', ff_opt: 'audio_input', type: 'select', values: [ 'embedded', 'aes_ebu', 'analog', 'analog_xlr', 'analog_rca', 'microphone', 'unset' ] },
    { alias: 'Pixel format', ff_opt: 'raw_format', type: 'select', values: [ 'uyvy422', 'yuv422p10', 'argb', 'bgra', 'rgb10' ] },
    { alias: 'Audio channels', ff_opt: 'channels', type: 'select', values: [ '2', '8', '16' ] },
    { alias: 'Duplex mode', ff_opt: 'duplex_mode', type: 'select', values: [ 'unset', 'half', 'full' ] },
    { alias: 'Video PTS source', ff_opt: 'video_pts', type: 'select', values: [ 'video', 'audio', 'reference', 'wallclock', 'abs_wallclock' ] },
    { alias: 'Audio PTS source', ff_opt: 'audio_pts', type: 'select', values: [ 'audio', 'video', 'reference', 'wallclock', 'abs_wallclock' ] },
    { alias: 'RT buffer size (Mb)', ff_opt: 'rtbufsize', type: 'number', values: 512 },
    { alias: 'Queue size (bytes)', ff_opt: 'queue_size', type: 'number', values: 4073741824 },
    { alias: 'Align timestamps (sec)', ff_opt: 'timestamp_align', type: 'number', values: 0 },
    { alias: 'Copy timestamps', ff_opt: 'decklink_copyts', type: 'checkbox', values: false }
  ];
  // SRT modes
  $scope.SRTModes = [
    { alias: 'Caller', value: 'caller' },
    { alias: 'Listener', value: 'listener' },
    { alias: 'Rendezvous', value: 'rendezvous' }
  ];
  // SRT Enc key length
  $scope.SRTpbkeylen = [
    { alias: '0', value: 0 },
    { alias: '16', value: 16 },
    { alias: '24', value: 24 },
    { alias: '32', value: 32 }
  ];
  // Video decoders
  $scope.VideoDecoders = [
    { alias: 'libavcodec', value: null },
    { alias: 'mpeg2_cuvid', value: 'mpeg2_cuvid' },
    { alias: 'h264_cuvid', value: 'h264_cuvid' }
  ];
  $scope.DecoderOptions = {
    Scale: { Value: null },
    Deinterlace: [
      { value: null, alias: 'None' },
      { value: 'bob', alias: 'Bob mode' },
      { value: 'adaptive', alias: 'Adaptive mode' }
    ]
  };
  $scope.ThumbnailsOptions = [
    { alias: 'None', value: null },
    { alias: 'libavcodec', value: 'libavcodec' },
    { alias: 'nvidia_cuda', value: 'cuvid' }
  ];
  // Decoders error detect level
  $scope.DecoderErrDetect = [
    { alias: 'None', value: null }, { alias: 'crccheck', value: 'crccheck' },
    { alias: 'bitstream', value: 'bitstream' }, { alias: 'buffer', value: 'buffer' },
    { alias: 'explode', value: 'explode' }, { alias: 'ignore_err', value: 'ignore_err' },
    { alias: 'careful', value: 'careful' }, { alias: 'compliant', value: 'compliant' },
    { alias: 'aggressive', value: 'aggressive'  }
  ];
  // Source activate
  $scope.SourceActive = { 'Main': true, 'Backup': false, 'Failover': false };
  // Default PID mapping matrix
  $scope.PIDMapping = [
    {
      SourceRole: 'Main',
      dbName: { video: 'main_vpid', audio: 'main_apid', data: 'main_dpid' }
    },
    {
      SourceRole: 'Backup',
      dbName: { video: 'bak_vpid', audio: 'bak_apid', data: 'bak_dpid' }
    },
    {
      SourceRole: 'Failover',
      dbName: { video: 'fail_vpid', audio: 'fail_apid', data: 'fail_dpid' }
    }
  ];
  // Screenshot failover source
  //$scope.SSFailover = '/images/ss_failover_uencode.png';
  //$scope.SSFailover = '/images/ss_failover_umedialink.png';
  $scope.SSFailover = '/images/ss_failover_pipencoder.png';
  // Pagination
  $scope.MaxPages = 10;
  // Presets data
  $scope.Presets = {};
  // Top navbar settings
  $scope.EditSettings = { JobStart: false, SaveData: false, KeepOpen: false };
  // Supported filters logic
  $scope.FilterTypes = [
    { 'alias': 'AND', 'value': 'and' },
    { 'alias': 'OR', 'value': 'or' }
  ];
  // Target select options
  $scope.TargetOptions = {
    HLSSegmentFormat: [
      { value: null, alias: 'ALL' },
      { value: 'Timestamp', alias: 'Timestamp' },
      { value: 'Sequence', alias: 'Sequence' }
    ]
  }
  // Supported video codec options
  $scope.vFilterOptions = {
    Deinterlace: [
      { value: null, alias: 'ALL' },
      { value: null, alias: 'None' },
      { value: 'send_frame', alias: 'Frame->Frame (source fps)' },
      { value: 'send_field', alias: 'Field->Frame (double fps)' },
      { value: 'send_frame_nospatial', alias: 'Frame->Frame (no spatial)' },
      { value: 'send_field_nospatial', alias: 'Field->Frame (no spatial)' }
    ],
    Scale: [
      { value: null, alias: 'ALL' },
      { value: null, alias: 'Original' },
      { value: '320x240', alias: '320x240' },
      { value: '480x360', alias: '480x360' },
      { value: '640x480', alias: '640x480' },
      { value: '720x404', alias: '720x404' },
      { value: '720x480', alias: '720x480' },
      { value: '720x576', alias: '720x576' },
      { value: '1280x720', alias: '1280x720' },
      { value: '1920x1080', alias: '1920x1080' },
      { value: '3840x2160', alias: '3840x2160' },
      { value: '4096x2160', alias: '4096x2160' },
      { value: 'Custom', alias: 'Custom' }
    ]
  };
  // Supported filters and sort-by options
  $scope.FilterList = {
  // TODO: Create FilterFilstUpdate() with updating filter properties on the go
    //{ field: 'all', alias: 'ALL', sort_by: true },
    id: { role: 'ALL', field: 'id', alias: 'Job ID' },
    sid: { role: 'ALL', field: 'sid', alias: 'Job ID (custom)' },
    job_name: { role: 'ALL', field: 'job_name', alias: 'Job name' },
    source_main: { role: 'sort_by', field: 'source_main', alias: 'Job Source' },
    source_global: { role: 'filter', field: 'source_global', alias: 'Job Source(s)' },
    target_global: { role: 'filter', field: 'target_global', alias: 'Job Target(s)' },
    run_status: { role: 'ALL', field: 'run_status', alias: 'Job Status',
      options: [
        { value: null, alias: 'ALL' },
        { value: 'OK', alias: 'OK' },
        { value: 'OFF', alias: 'OFF' },
        { value: 'UPD', alias: 'Update/Check' },
        { value: 'ERR', alias: 'All errors' },
        { value: 'ERR_SRC', alias: 'Source errors' },
        { value: 'ERR_ENC', alias: 'Encode errors' }
      ]
    },
    retries: { role: 'ALL', field: 'retries', alias: 'Job Retries' },
    uptime: { role: 'sort_by', field: 'uptime', alias: 'Job Uptime' },
    video_pid_global: { role: 'filter', field: 'video_pid_global', alias: 'Video PID(s)' },
    audio_pid_global: { role: 'filter', field: 'audio_pid_global', alias: 'Audio PID(s)' },
    data_pid_global: { role: 'filter', field: 'data_pid_global', alias: 'SCTE35 PID(s)' },
    vpreset: { role: 'filter', field: 'vpreset', alias: 'Video Preset',
      options: [
        { value: null, alias: 'ALL' }
      ]
    },
    apreset: { role: 'filter', field: 'apreset', alias: 'Audio Preset',
      options: [
        { value: null, alias: 'ALL' }
      ]
    },
    venc_psize: { role: 'filter', field: 'venc_psize', alias: 'Frame size', options: $scope.vFilterOptions.Scale },
    venc_di: { role: 'filter', field: 'venc_di', alias: 'Deinterlace', options: $scope.vFilterOptions.Deinterlace },
    nvenc_gpu: { role: 'filter', field: 'nvenc_gpu', alias: 'GPU Powered',
      options: [
        { value: null, alias: 'ALL' },
        { value: 'auto', alias: 'Auto balance' },
        { value: 'none', alias: 'Not GPU' }
      ]
    },
    stream_type: { role: 'filter', field: 'stream_type', alias: 'Stream type',
      options: [
        { value: null, alias: 'ALL' },
        { value: 'UDP', alias: 'UDP' },
        { value: 'HLS', alias: 'HLS' },
        { value: 'RTMP', alias: 'RTMP' }
        //, { value: 'Smooth', alias: 'Smooth' }
      ]
    },
    stream_srv: { role: 'filter', field: 'stream_srv', alias: 'Stream Server',
      options: [
        { value: null, alias: 'ALL' }
      ]
    },
    hls_abr_active: { role: 'filter', field: 'hls_abr_active', alias: 'HLS ABR Active',
      options: [
        { value: null, alias: 'ALL' },
        { value: '1', alias: 'Yes' },
        { value: '0', alias: 'No' }
      ]
    },
    hls_drm_active: { role: 'filter', field: 'hls_drm_active', alias: 'HLS DRM Protected',
      options: [
        { value: null, alias: 'ALL' },
        { value: '1', alias: 'Yes' },
        { value: '0', alias: 'No' }
      ]
    }
  };
  /// End of Variables init ///


  $window.onresize = function(event) {
    var Mode = $rootScope.GUI.Jobs.Layout.Mode;
    if ($window.innerWidth < 992 && Mode == 'List') {
      $rootScope.GUI.Jobs.Layout[Mode].Index = 1;
    } else {
      $rootScope.GUI.Jobs.Layout[Mode].Index = $rootScope.GUI.Jobs.Layout[Mode].IndexPrev;
    }
  };


  // FilterList role mapping
  $scope.FilterListRole = function(Role) {
    return function(FilterItem) {
      return (FilterItem.role == Role || FilterItem.role == 'ALL');
    };
  }


  $scope.GPUInit = function(GPUData) {
    $log.debug('GPUInit: ', GPUData);
    $scope.GPUList = [];
    $scope.GPUOptionsShow = false;
    if (GPUData.dev_count > 0) {
      $scope.GPUList.push({ 'ID': 'auto', 'Name': 'Auto balance', 'Active': true });
      var DeviceData = GPUData.dev_data;
      DeviceData.splice(0, 1);
      $log.debug('GPUInit: DeviceData', DeviceData);
      if (DeviceData) {
        for (idx in DeviceData) {
          var Device = DeviceData[idx];
          var GPUStringID = idx.toString();
          var GPUDevName = Device.dev_name + ' (' + GPUStringID + ')';
          $scope.GPUList.push({ ID: GPUStringID, Name: GPUDevName, Active: Device.active });
          $scope.FilterList.nvenc_gpu.options.push({ value: GPUStringID, alias: GPUDevName });
        }
      }
      $scope.GPUOptionsShow = true;
    }
    $log.debug('GPUList: ', $scope.GPUList);
  }


  // Screen layout mode set: Monitor or List
  $scope.ScreenLayoutModeSet = function() {
    var Mode = $rootScope.GUI.Jobs.Layout.Mode;
    Mode == 'Monitor' ? Mode = 'List' : Mode = 'Monitor';
    $rootScope.GUI.Jobs.Layout.Mode = Mode;
    LSM.Save({ GUI: $rootScope.GUI });
    $log.debug('ScreenLayoutModeSet', Mode);
  }


  // Set active layout index
  $scope.ScreenLayoutIndexSet = function(Action) {
    var Mode = $rootScope.GUI.Jobs.Layout.Mode;
    var Index = $rootScope.GUI.Jobs.Layout[Mode].Index;
    var IndexMax = $rootScope.GUI.Jobs.Layout[Mode].IndexMax;
    if (Action == 'up') {
      if (Index < IndexMax) { Index +=1; } else { Index = IndexMax; }
    } else {
      if (Index > 0) { Index -= 1; } else { Index = 0; }
    }
    $rootScope.GUI.Jobs.Layout[Mode].Index = Index;
    $rootScope.GUI.Jobs.Layout[Mode].IndexPrev = Index;
    $log.debug('ScreenLayoutIndexSet: Index', Index);
    LSM.Save({ GUI: $rootScope.GUI });
  }


  // Apply bootstrap grid classes
  $scope.ScreenLayoutApply = function(Index) {
    var Style = '';
    var Mode = $rootScope.GUI.Jobs.Layout.Mode;
    var Index = $rootScope.GUI.Jobs.Layout[Mode].Index;
    var Grid = 12 / $rootScope.GUI.Jobs.Layout[Mode].Grid[Index];
    if (Mode == 'Monitor') {
      if (Index == 1) { xs = ' col-xs-2'; sm = ' col-sm-2'; } else { xs = ' col-xs-' + Grid; sm = ' col-sm-' + Grid; }
      Style = xs + sm + ' col-md-' + Grid + ' col-lg-' + Grid + ' ';
    } else {
      if (Index == 0) { lg = ' col-lg-3'; } else { lg = ' col-lg-' + Grid; }
      Style = ' col-md-' + Grid + lg + ' ';
    }
    return Style;
  }


  // Map active Job PIDs to MediaInfo stream list
  $scope.MediaInfoCodecParse = function(Stream, ProgramHas) {
    if (Stream.codec_type == 'video') {
      ProgramHas.Video = true;
  //    $scope.Profile.SourceHas.Video = true;
      Stream.Stats = Stream.codec_name + ' [ ' + Stream.width + 'x' + Stream.height + ' (' + Stream.display_aspect_ratio + '), ' + Stream.r_frame_rate + ' fps ]';
    }
    if (Stream.codec_type == 'audio') {
      ProgramHas.Audio = true;
  //    $scope.Profile.SourceHas.Audio = true;
      Stream.Stats = Stream.codec_name + ' [ ' + Stream.channels + ' ch / ' + Stream.channel_layout + ', ' + Stream.bit_rate + ' kbps, ' + Stream.sample_rate + ' Hz ]';
    }
    if (Stream.codec_type == 'data') {
      ProgramHas.BinData = true;
  //    $scope.Profile.SourceHas.Binary = true;
    }
  }


  // Check Youtube streams expiration date
  $scope.MediaInfoYTExpireDate = function(URL) {
    var UTCSeconds = Math.round(new Date() / 1000);
    if (URL.includes('?') && URL.includes('&')) {
      var YTURLSplit = URL.split('?');
      YTURLSplit = YTURLSplit[1].split('&');
      YTURLSplit.forEach(function(value) {
        value = value.split('=');
        value[0] == 'expire' ? UTCSeconds = value[1] : null;
      });
    } else {
      var YTURLSplit = URL.split('/');
      YTURLSplit.forEach(function(value, key) {
        value == 'expire' ? UTCSeconds = YTURLSplit[key + 1] : null;
      });
    }
    return UTCSeconds;
  }


  // Parse MediaInfo data (programs/streams)
  $scope.MediaInfoProgramParse = function(Programs, Source, YTSource) {
    $scope.MediaInfo.MediaExt = Source.dbName.MediaExt;
    // Loop through Tracks/Programs/Streams
    for (p_idx in Programs) {
      var Program = Programs[p_idx];
      if (YTSource) {
        Program.expire = $scope.MediaInfoYTExpireDate(Program.url);
        Program.valid_for = $scope.ExpireDateHMS(Program.expire);
        Program.isCollapsed = true;
      } else {
        Program.isCollapsed = false;
      }
      Program.Has = { Video: false, Audio: false, BinData: false };
      var Streams = Program.streams;
      for (s_idx in Streams) {
        var Stream = Streams[s_idx];
        if (Stream.id != null) { Stream.id = parseInt(Stream.id, 16); }
        if (Stream.bit_rate) { Stream.bit_rate = Math.round(Stream.bit_rate/1000); }
        Stream.r_frame_rate = Math.round(eval(Stream.r_frame_rate) * 100) / 100;
        Stream.SourceRole = Source.Role;
        $scope.MediaInfoCodecParse(Stream, Program.Has);
        if (YTSource) {
          var SourceMediaExt = $scope.ActiveJob.job_data[Source.dbName.MediaExt];
          if (SourceMediaExt) {
            Stream.Selected = (Program.program_id == SourceMediaExt.format_id) || false;
            Program.isCollapsed = Stream.Selected ? false : true;
          }
        } else {
          $scope.PIDMapProfileToMIStream(Stream, $scope.ActiveJob.profile[$scope.Profile.Active]);
        }
        // Create Stream(s) list
        $scope.MediaInfo.Streams.push(Stream);
        Streams[s_idx] = Stream;
      }
      Program.streams = Streams;
      Programs[p_idx] = Program;
    }
    return Programs;
  }


  function PadNumber(number, letter) {
    return (number < 10 ? letter : '') + number
  }


  // Convert UTC to HMS format
  $scope.ExpireDateHMS = function(UTCSeconds) {
    var DateNow = new Date();
    var ExpiredDate = new Date(UTCSeconds * 1000);
    var diffMs = (ExpiredDate - DateNow); // milliseconds
    var diffHrs = PadNumber(Math.floor((diffMs % 86400000) / 3600000), '0'); // hours
    var diffMins = PadNumber(Math.round(((diffMs % 86400000) % 3600000) / 60000), '0'); // minutes
    var diffSecs = PadNumber(Math.round(((diffMs % 86400000) % 3600000) / 360000), '0'); // seconds
    return diffHrs + ':' + diffMins + ':' + diffSecs;
  }


  /*// Parse MediaInfo Youtube streams
  $scope.MediaInfoYTStreamParse = function(MediaData, Source) {
    var Streams = MediaData.streams;
    for (sIDX in Streams) {
      var Stream = Streams[sIDX];
      var SourceMediaExt = $scope.ActiveJob.job_data[Source.dbName.MediaExt];
      if (SourceMediaExt) {
        Stream.Selected = (Stream.format_id == SourceMediaExt.format_id) || false;
      }
      Stream.SourceRole = Source.Role;
      Stream.expire = $scope.MediaInfoYTExpireDate(Stream.url);
      Stream.valid_for = $scope.ExpireDateHMS(Stream.expire);
      Streams[sIDX] = Stream;
    }
    $log.debug('MediaInfoYTStreamParse Streams: ', Streams);
    return Streams;
  }
  */

  // Media info
  $scope.MediaInfoGetData = function(Source) {
    $scope.MediaInfoReset();
    var Media = Source.Media[Source.Media.Type] || null;
    var MediaType = Source.Media.Type || null;
    Source.Analyzing = true;
    $log.debug('MediaInfoGetData Media: ', Media, 'MediaType: ', MediaType);
    $http.post('/api/v1/media/info', { media: Media, media_type: MediaType })
    .then(
      function(success) {
        $log.debug('MediaInfoGetData Response: ', success);
        var SourceMD = success.data;
        var MediaData = SourceMD.programs || [ { program_id: null, streams: SourceMD.streams } ];
        $log.debug('MediaInfoGetData MediaData: ', MediaData);
        if (Media.includes('://www.youtube.com')) {
          $scope.MediaInfo.YTStream = true;
        }
        $scope.MediaInfo.Programs = $scope.MediaInfoProgramParse(MediaData, Source, $scope.MediaInfo.YTStream);
        $scope.MediaInfo.Show = true;
        $log.debug('MediaInfoGetData MediaInfo: ', $scope.MediaInfo);
      },
      function(error) {
        $log.error('MediaInfoGetData Response: ', error);
        Alerts.Add('jobs', 'danger', 'MediaInfo: ' + error.statusText);
      }
    )
    .finally(function() {
      Source.Analyzing = false;
    });
  }


  // Map active Job PIDs to MediaInfo stream
  $scope.PIDMapProfileToMIStream = function(Stream, Profile) {
    for (PID in $scope.PIDMapping) {
      var PID = $scope.PIDMapping[PID];
      if (PID.SourceRole == Stream.SourceRole && Profile[PID.dbName[Stream.codec_type]]) {
        if (Profile[PID.dbName[Stream.codec_type]] == ('#' + Stream.id) ||
            Profile[PID.dbName[Stream.codec_type]] == Stream.index)
          {
            Stream.Selected = true;
          } else {
            Stream.Selected = false;
          }
      }
    }
  }


  // Map active Job PIDs to MediaInfo all stream
  $scope.PIDMapProfileToMIStreamList = function(Profile) {
    for (MIS in $scope.MediaInfo.Streams) {
      $scope.PIDMapProfileToMIStream($scope.MediaInfo.Streams[MIS], $scope.ActiveJob.profile[Profile]);
    }
  }


  // Clear MediaInfo stream list selection
  $scope.MediaInfoStreamListClear = function(Stream) {
    if (Stream.Selected) {
      for (MIS in $scope.MediaInfo.Streams) {
        var MIS = $scope.MediaInfo.Streams[MIS];
        if (MIS != Stream && MIS.codec_type == Stream.codec_type) {
          MIS.Selected = false;
        }
      }
    }
  }


  // Map MediaInfo stream data to all Profiles
  $scope.MediaInfoStreamSelect = function(Program, Stream, Profile) {
    // Default new "PID = null" applies if stream is un-checked
    var PID = null;
    Stream.Selected = !Stream.Selected;
    $scope.MediaInfoStreamListClear(Stream);
    if (Stream.Selected) {
      // YT stream
      if ($scope.MediaInfo.YTStream) {
        $scope.ActiveJob.job_data[$scope.MediaInfo.MediaExt] = {
          format_id: Program.program_id,
          url: Program.url,
          expire: Program.expire
        };
      }
      $scope.Profile.Stats[Stream.codec_type] = Stream.Stats;
      if (Stream.id == null) { PID = Stream.index; } else { PID = '#' + Stream.id; }
      $scope.Profile.Options[Profile].EncoderActive[Stream.codec_type] = true;
      $log.debug('MediaInfoStreamSelect: EncoderActive: ', $scope.Profile.Options[Profile].EncoderActive);
    } else {
      // Reset MediaInfo stats for all Profiles
      $scope.ActiveJob.job_data[$scope.MediaInfo.MediaExt] = null;
      $scope.Profile.Stats[Stream.codec_type] = $scope.MediaInfo.DefaultInfo;
    }
    $scope.ProfilePIDChangeByGroup(PID, $scope.ActiveJob.profile, Stream.SourceRole, Stream.codec_type);
    $log.debug('MediaInfoStreamSelect: Stream: ', Stream, ', Profile: ', Profile);
  }

  /*
  // Youtube ID and manifest to active Job
  $scope.MediaInfoStreamSelectYT = function(Stream) {
    Stream.Selected = !Stream.Selected;
    $scope.MediaInfoStreamListClear(Stream);
    if (Stream.Selected) {
      $scope.ActiveJob.job_data[$scope.MediaInfo.MediaExt] = {
        format_id: Stream.format_id,
        url: Stream.url,
        expire: Stream.expire
        //valid_for: Stream.valid_for
      };
    } else {
      $scope.ActiveJob.job_data[$scope.MediaInfo.MediaExt] = null;
    }
    var EncActive = { video: Stream.vcodec ? true : false, audio: Stream.acodec ? true : false };
    $scope.Profile.Options[$scope.Profile.Active].EncoderActive = EncActive;
    $scope.ProfilePIDChangeByGroup(null, $scope.ActiveJob.profile, null, null);
    $log.debug('MediaInfoStreamSelect: Stream: ', Stream, ', ActiveJob: ', $scope.ActiveJob);
  }
  */

  // Reset MediaInfo table
  $scope.MediaInfoReset = function() {
    $scope.MediaInfo = { Show: false, YTStream: false, Streams: [], DefaultInfo: 'Please select a stream' };
  }


  // Get media list
  $scope.GetMediaSourceLocal = function(ActiveJob) {
    $http.post('/api/v1/media/local')
    .then(
      function(success) {
        $log.debug('GetMediaSourceLocal response:', success);
        var data = success.data;
        $scope.MediaSourceLocal = { Assets: data.assets, Devices: data.devices };
        $scope.SourceInit(ActiveJob, data);
      },
      function(error) {
        $log.error('GetMediaSourceLocal response:', error);
        Alerts.Add('jobs', 'danger', 'Load media: ' + error.statusText);
      }
    );
  }


  // Set default Source values
  $scope.SourceDefault = function() {
    return [
      {
        Role: 'Main',
        Media: { Type: 'URL', URL: null, Image: null, Clip: null },
        Active: true,
        Analyzing: false,
        Options: {},
        dbName: {
          Media: 'source_main',
          MediaExt: 'source_main_ext',
          MediaType: 'source_main_type',
          vDecoder: 'source_main_decoder',
          DecoderErrDetect: 'source_main_decoder_err_detect',
          DecoderDeinterlace: 'source_main_decoder_deinterlace',
          DecoderScale: 'source_main_decoder_scale',
          Loop: 'source_main_loop',
          UDPBuffer: 'source_main_udp_buffer',
          UDPTimeout: 'source_main_udp_timeout',
          UDPOverrun: 'source_main_udp_overrun',
          SRTMode: 'source_main_srt_mode',
          SRTPassphrase: 'source_main_srt_passphrase',
          HTTPReconnect: 'source_main_http_reconnect',
          MergePMTVersions: 'source_main_merge_pmt_versions'
        }
      },
      {
        Role: 'Backup',
        Media: { Type: 'URL', URL: null, Image: null, Clip: null },
        Active: false,
        Analyzing: false,
        Options: {},
        dbName: {
          Media: 'source_bak',
          MediaExt: 'source_bak_ext',
          MediaType: 'source_bak_type',
          vDecoder: 'source_bak_decoder',
          DecoderErrDetect: 'source_bak_decoder_err_detect',
          DecoderDeinterlace: 'source_bak_decoder_deinterlace',
          DecoderScale: 'source_bak_decoder_scale',
          Loop: 'source_bak_loop',
          UDPBuffer: 'source_bak_udp_buffer',
          UDPTimeout: 'source_bak_udp_timeout',
          UDPOverrun: 'source_bak_udp_overrun',
          SRTMode: 'source_bak_srt_mode',
          SRTPassphrase: 'source_bak_srt_passphrase',
          HTTPReconnect: 'source_bak_http_reconnect',
          MergePMTVersions: 'source_bak_merge_pmt_versions'
        }
      },
      {
        Role: 'Failover',
        Media: { Type: 'Default', URL: null, Image: null, Clip: null },
        Active: false,
        Analyzing: false,
        Options: {},
        dbName: {
          Media: 'source_fail',
          MediaExt: 'source_fail_ext',
          MediaType: 'source_fail_type',
          vDecoder: 'source_fail_decoder',
          DecoderErrDetect: 'source_fail_decoder_err_detect',
          DecoderDeinterlace: 'source_fail_decoder_deinterlace',
          DecoderScale: 'source_fail_decoder_scale',
          Loop: 'source_fail_loop',
          UDPBuffer: 'source_fail_udp_buffer',
          UDPTimeout: 'source_fail_udp_timeout',
          UDPOverrun: 'source_fail_udp_overrun',
          SRTMode: 'source_fail_srt_mode',
          SRTPassphrase: 'source_fail_srt_passphrase',
          HTTPReconnect: 'source_fail_http_reconnect',
          MergePMTVersions: 'source_fail_merge_pmt_versions'
        }
      }
    ];
  }

  // Set 'Default' source value only for Failover source
  $scope.SourceFilter = function(source_role) {
    return function(item) {
      if (source_role == 'Failover') {
        return true;
      } else {
        if (item == 'Default') {
          return false;
        }
        return true;
      }
    };
  };


  function StringContains(target, pattern){
    var value = 0;
    pattern.forEach(function(word) {
      value = value + target.includes(word);
    });
    return (value === 1);
  }


  // Show source extra options
  $scope.SourceOptionsApply = function(Source) {
    Source.Options.UDPShow = false;
    Source.Options.HTTPShow = false;
    Source.Options.MPEGTSShow = false;
    Source.Options.YTShow = false;
    //$scope.ActiveJob.job_data[Source.dbName.MediaExt] = {};
    $scope.ShowProfilePID = true;
    if (Source.Media[Source.Media.Type]) {
      if (Source.Media.Type != 'Device') {
        if (StringContains(Source.Media[Source.Media.Type], [ 'udp://' ])) {
          Source.Options.UDPShow = true;
        }
        if (StringContains(Source.Media[Source.Media.Type], [ 'srt://' ])) {
          Source.Options.SRTShow = true;
        }
        if (StringContains(Source.Media[Source.Media.Type], [ 'http://', 'https://' ])) {
          Source.Options.HTTPShow = true;
        }
        if (StringContains(Source.Media[Source.Media.Type], [ 'udp://', 'srt://', '.ts', '.mpeg', '.mpg' ])) {
          Source.Options.MPEGTSShow = true;
        }
        if (StringContains(Source.Media[Source.Media.Type], [ '://www.youtube.com' ])) {
          Source.Options.YTShow = true;
          //$scope.ShowProfilePID = false;
        }
      } else {
        //$log.debug('SourceLocalData:', $scope.MediaSourceLocal.Devices);
        for (DevOpt in $scope.MediaSourceLocal.Devices) {
          device = $scope.MediaSourceLocal.Devices[DevOpt];
          if (device.name == Source.Media.Device) {
            $scope.DecklinkStatus = device.status;
            $scope.Decklink[0].values = device.format_code;
            if (!(Source.dbName.MediaExt in $scope.ActiveJob.job_data)) {
              var SourceExt = {};
              SourceExt[device.name] = { brand: device.brand };
              $scope.Decklink.forEach(function(DL) {
                if (DL.values != undefined) {
                  SourceExt[device.name][DL.ff_opt] = (DL.type == 'select') ? DL.values[0] : DL.values;
                }
              });
              $scope.ActiveJob.job_data[Source.dbName.MediaExt] = SourceExt;
            }
          }
        }
        $scope.ShowProfilePID = false;
        $log.debug('Decklink:', $scope.MediaSourceLocal.Devices);
        $log.debug('Decklink:', $scope.Decklink);
        $log.debug('ActiveJob:', $scope.ActiveJob);
      }
    }
  }


  // Init edit dialog with Source values
  $scope.SourceInit = function(ActiveJob, SourceLocalData) {
    var Sources = $scope.SourceDefault();
    for (src_idx in Sources) {
      // Set default source mapping if no value is defined
      var Source = Sources[src_idx];
      var ActiveJobMedia = ActiveJob.job_data[Source.dbName.Media];
      // Apply source values from ActiveJob if any
      Source.Media.Image = SourceLocalData.assets.images[0];
      Source.Media.Clip = SourceLocalData.assets.clips[0];
      Source.Media.Device = SourceLocalData.devices.length ? SourceLocalData.devices[0].name : 'No available device(s)';
      Source.Media.URL = null;
      if (ActiveJobMedia == 'default') {
        Source.Active = true;
        $scope.SourceActive[Source.Role] = false;
      }
      if (ActiveJobMedia && (ActiveJobMedia != 'default')) {
        Source.Active = true;
        Source.Media[ActiveJob.job_data[Source.dbName.MediaType]] = ActiveJobMedia;
        Source.Media.Type = ActiveJob.job_data[Source.dbName.MediaType];
        $scope.SourceActive[Source.Role] = Source.Active;
      }
      $scope.SourceOptionsApply(Source);
      Sources[src_idx] = Source;
    }
    $scope.Sources = Sources;
    $log.debug('SourceInit: Sources:', $scope.Sources);
  }

  /*
  $scope.DecklinkSelect = function() {
    $log.debug('ActiveJob: ', $scope.ActiveJob);
  }
  */

  // Select a Source type and apply changes back to ActiveJob model
  $scope.SourceSelect = function(Source, ActiveJob) {
    $scope.MediaInfoReset();
    $scope.SourceOptionsApply(Source);
    $scope.SourceActive[Source.Role] = Source.Active;
    ActiveJob.job_data[Source.dbName.Media] = null;
    ActiveJob.job_data[Source.dbName.MediaType] = Source.Media.Type;
    if (Source.Active) {
      if (Source.Media.Type == 'Default') {
        ActiveJob.job_data[Source.dbName.Media] = 'default';
        $scope.SourceActive[Source.Role] = false;
      } else if (Source.Media[Source.Media.Type]) {
        ActiveJob.job_data[Source.dbName.Media] = Source.Media[Source.Media.Type];
        //ActiveJob.job_data[Source.dbName.MediaExt] = {};
      }
    } else {
      $scope.ProfilePIDChangeByGroup(null, ActiveJob.profile, Source.Role, null);
    }
    $log.debug('SourceSelect: Source:', Source);
  }


  // Filter video decoders capabilities
  $scope.GPUEnabledFilter = function() {
    return function(decoder) {
      var DecoderActive = true;
      if (decoder.value && decoder.value.includes('cuvid')) {
        DecoderActive = false;
        if ($scope.GPUOptionsShow) { DecoderActive = true; }
      }
      return DecoderActive;
    }
  }


  // Get last user defined ID (used for Job editing)
  $scope.JobLastUserID = function() {
    return ($scope.Jobs.List.length ? $scope.Jobs.List[$scope.Jobs.List.length - 1].job_data.sid : 0);
  }


  // Set default Job values
  $scope.JobDataDefault = function() {
    return {
      job_data: {
        job_name: null,
        abort_on_empty_output: true,
        ignore_unknown: true,
        max_error_rate: 0.75,
        check_timeout: 20,
        check_source: true,
        check_target: true,
        thumb_render: 'libavcodec',
        thumb_interval: 50,
        source_main: null,
        source_main_udp_overrun: true,
        source_main_srt_mode: $scope.SRTModes[0].value,
        source_main_http_reconnect: true,
        source_main_merge_pmt_versions: false,
        source_bak_udp_overrun: true,
        source_bak_srt_mode: $scope.SRTModes[0].value,
        source_bak_http_reconnect: true,
        source_bak_merge_pmt_versions: false,
        source_fail_udp_overrun: true,
        source_fail_srt_mode: $scope.SRTModes[0].value,
        source_fail_http_reconnect: true,
        source_fail_merge_pmt_versions: false,
        source_main_decoder: $scope.VideoDecoders[0].value,
        source_main_decoder_err_detect: $scope.DecoderErrDetect[0].value,
        source_main_decoder_deinterlace: $scope.DecoderOptions.Deinterlace[0].value,
        source_main_decoder_scale: $scope.vFilterOptions.Scale[1].value,
        source_bak_decoder: $scope.VideoDecoders[0].value,
        source_bak_decoder_err_detect: $scope.DecoderErrDetect[0].value,
        source_bak_decoder_deinterlace: $scope.DecoderOptions.Deinterlace[0].value,
        source_bak_decoder_scale: $scope.vFilterOptions.Scale[1].value,
        source_fail_decoder: $scope.VideoDecoders[0].value,
        source_fail_decoder_err_detect: $scope.DecoderErrDetect[0].value,
        source_fail_decoder_deinterlace: $scope.DecoderOptions.Deinterlace[0].value,
        source_fail_decoder_scale: $scope.vFilterOptions.Scale[1].value,
        source_active: 'main',
        source_main_type: 'URL',
        source_main_bak_rr: true,
        hls_abr_server: Object.keys($scope.Servers.List)[0],
        hls_drm_active: false,
        hls_drm_type: $scope.DRMTypes[0],
        hls_drm_key_type: 'Local',
        sid : $scope.JobLastUserID() + 1
      },
      profile: [ $scope.ProfileDataDefault() ]
    };
  }


  // Reset Job Edit dialog to default values
  $scope.JobOptionsDefault = function() {
    // Global Profile variables
    $scope.Profile = {
      Active: '0',
      // Init encoder edit settings
  //    SourceHas: { Video: true, Audio: true, Binary: true },
      // Init Profile == 'Copy' short details (MediaInfo active stream)
      Stats: { video: $scope.MediaInfo.DefaultInfo, audio: $scope.MediaInfo.DefaultInfo },
      // Profile delete confirm request
      DeleteConfirm: false,
      // Profile(s) options array
      Options: []
    };
    // Active Target operation
    $scope.Target = { DeleteConfirm: false, Active: '0' };
  }


  // Set default Profile values
  $scope.ProfileDataDefault = function() {
     profile_default = {
      'main_vpid': null,
      'main_apid': null,
      'vpreset': 'H264_650',
      'apreset': 'AAC_LC_64',
      'dpreset': 'copy',
  // TODO: make use gpu = null by default, check on Profile change
      'nvenc_gpu': 'none',
      'venc_psize': null,
      'venc_di': null,
      'target': [ $scope.TargetDataDefault() ]
    };
    return profile_default;
  }


  // Reset ProfileOptions to default values
  $scope.ProfileOptionsDefault = function() {
    return {
      EncoderActive: { video: false, audio: false, data: false },
      isGPUProfile: false,
      vFilters: {
        Scale: { Value: null }
      }
    }
  }


  // Init Profile options
  $scope.ProfileOptionsInit = function(ActiveJob) {
    Profiles = ActiveJob.profile;
    // Mapping DB data to local Profile options array (Profile.Options)
    for (Profile in Profiles) {
      // Add default Profile options value
      $scope.Profile.Options.push($scope.ProfileOptionsDefault());
      // Get actual video preset data
      var vPresetData = $scope.PresetDataGet(Profiles[Profile].vpreset, 'video');
      // Check if Profile is GPU capable (NVENC only)
      if (vPresetData) {
        var isGPUProfile = $scope.vPresetGPUCheck(vPresetData.vcodec);
        if (isGPUProfile) {
          //Profiles[Profile].nvenc_gpu = 'auto';
        } else {
          Profiles[Profile].nvenc_gpu = 'none';
        }
        $scope.Profile.Options[Profile].isGPUProfile = isGPUProfile;
      }
      // Video filters data init
      $scope.ProfilevFiltersInit(Profiles[Profile], $scope.Profile.Options[Profile]);
      // Activate associated encoder by PID type (if PID is not null)
      for (PID in $scope.PIDMapping) {
        var PID = $scope.PIDMapping[PID];
        Object.keys(PID.dbName).forEach(function(key) {
          if (Profiles[Profile][PID.dbName[key]] != null || ActiveJob.job_data.source_main_ext) {
            $scope.Profile.Options[Profile].EncoderActive[key] = true;
          }
        });
      }
      for (Target in Profiles[Profile].target) {
        $scope.ABRMetadataParse(ActiveJob, Profile, Target);
      }
    }
  }


  // Apply selected encoder options
  $scope.ProfileEncoderSelect = function(Profile, AVType) {
    if (AVType != 'data') {
      $scope.PresetSelect(AVType);
    }
    if (!$scope.Profile.Options[Profile].EncoderActive[AVType]) {
      $scope.ProfilePIDChange(null, $scope.ActiveJob.profile[Profile], null, AVType);
      $scope.PIDMapProfileToMIStreamList(Profile);
    }
  }


  // Init edit dialog with video filters values
  $scope.ProfilevFiltersInit = function(Profile, ProfileOption) {
    // Map custom scale option
    var ScaleCustomFound = true;
    for (psize in $scope.vFilterOptions.Scale) {
      if (Profile.venc_psize == $scope.vFilterOptions.Scale[psize].value) {
        ProfileOption.vFilters.Scale.Value = Profile.venc_psize;
        ScaleCustomFound = false;
      }
    }
    if (ScaleCustomFound) {
      var scale_split = Profile.venc_psize.split('x');
      ProfileOption.vFilters.Scale.Value = 'Custom';
      ProfileOption.vFilters.Scale.Width = parseInt(scale_split[0]);
      ProfileOption.vFilters.Scale.Height = parseInt(scale_split[1]);
    }
  }


  // Activate custom scale controls
  $scope.ProfileCustomScaleSelect = function(profile) {
    if ($scope.Profile.Options[profile].vFilters.Scale.Value == 'Custom') {
      // Merge custom scale values to a single string
      var CustomWidth = ($scope.Profile.Options[profile].vFilters.Scale.Width || '[width]');
      var CustomHeight = ($scope.Profile.Options[profile].vFilters.Scale.Height || '[height]');
      $scope.ActiveJob.profile[profile].venc_psize = CustomWidth + 'x' + CustomHeight;
    } else {
      $scope.ActiveJob.profile[profile].venc_psize = $scope.Profile.Options[profile].vFilters.Scale.Value;
    }
    $scope.ActiveJob.profile[profile].target[$scope.Target.Active].hls_abr_resolution = $scope.ActiveJob.profile[profile].venc_psize;
    $scope.ABRMetadataBuild($scope.ActiveJob);
  }


  // Activate custom scale controls
  $scope.DecoderCustomScaleSelect = function(Source) {
    if ($scope.DecoderOptions.Scale.Value == 'Custom') {
      // Merge custom scale values to a single string
      var CustomWidth = $scope.DecoderOptions.Scale.Width || '[width]';
      var CustomHeight = $scope.DecoderOptions.Scale.Height || '[height]';
      $scope.ActiveJob.job_data[Source.dbName.DecoderScale] = CustomWidth + 'x' + CustomHeight;
    } else {
      $scope.ActiveJob.job_data[Source.dbName.DecoderScale] = $scope.DecoderOptions.Scale.Value;
    }
    $log.debug('DecoderCustomScaleSelect: DecoderScale: ', $scope.ActiveJob.job_data[Source.dbName.DecoderScale]);
  }


  // Change PID(s) for selected Profile
  // Group filters: Source role (Main/Backup/Failover) and/or data type (video/audio/data)
  // "SourceRole = null" will process all Source roles
  // "DataType = null" will process all data types
  // Both "SourceRole = null && DataType = null" will process ALL PIDs
  $scope.ProfilePIDChange = function(PIDValue, Profile, SourceRole, DataType) {

    var PIDFilterByData = function() {
      if (DataType) {
        Profile[PID.dbName[DataType]] = PIDValue;
      } else {
        Profile[PID.dbName.video] = PIDValue;
        Profile[PID.dbName.audio] = PIDValue;
        Profile[PID.dbName.data] = PIDValue;
      }
    }

    for (PID in $scope.PIDMapping) {
      var PID = $scope.PIDMapping[PID];
      if (SourceRole) {
        if (PID.SourceRole == SourceRole) { PIDFilterByData(); }
      } else {
        PIDFilterByData();
      }
    }
  }


  // Change PID(s) for all Profiles. Check options description above.
  $scope.ProfilePIDChangeByGroup = function(PIDValue, JobProfiles, SourceRole, DataType) {
    for (Profile in JobProfiles) {
      $scope.ProfilePIDChange(PIDValue, JobProfiles[Profile], SourceRole, DataType);
    }
  }


  // New profile init in Edit dialog
  $scope.ProfileAdd = function(profile) {
    profile = parseInt(profile);
    profile = $scope.ActiveJob.profile.length;
    // Set default Profile values
    $scope.ActiveJob.profile[profile] = $scope.ProfileDataDefault();
    // Add default Profile options value
    $scope.Profile.Options.push($scope.ProfileOptionsDefault());
    $scope.Profile.Active = profile.toString();
    $scope.Target.Active = '0';
    $scope.AssetsPreviewBuild($scope.ActiveJob);
    $log.debug('ProfileAdd: ActiveJob Profiles: ', $scope.ActiveJob.profile);
  }


  // Delete a profile in Edit dialog
  $scope.ProfileDelete = function(profile) {
    profile = parseInt(profile);
    $scope.ActiveJob.profile.splice(profile, 1);
    if (profile == $scope.ActiveJob.profile.length) { profile = profile - 1; }
    $scope.Profile.DeleteConfirm = false;
    $scope.Profile.Active = profile.toString();
    $scope.Target.Active = '0';
    $scope.AssetsPreviewBuild($scope.ActiveJob);
    $log.debug('ProfileDelete: ActiveJob Profiles: ', $scope.ActiveJob.profile);
  }


  // Change Profile actions
  $scope.ProfileChange = function(Profile) {
    $scope.Target.Active = '0';
    $scope.PIDMapProfileToMIStreamList(Profile);
    $scope.AssetsPreviewBuild($scope.ActiveJob);
  }


  // Set default Target values
  $scope.TargetDataDefault = function() {
    return {
      target_type: 'Stream',
      stream_srv: Object.keys($scope.Servers.List)[0],
      stream_type: 'HLS',
      stream_name: null,
      hls_list_size: 8,
      hls_seg_time: 8,
      hls_seg_format: 'Timestamp',
      hls_seg_name: '%Y%m%d%H%M%S',
      srt_mode: $scope.SRTModes[0].value,
      srt_pbkeylen: $scope.SRTpbkeylen[0].value,
      mpegts_pcr_period: 20,
      mpegts_pat_period: 0.1,
      mpegts_sdt_period: 0.5
    };
  }


  // New target init in Edit dialog
  $scope.TargetAdd = function(profile, target) {
    target = parseInt(target);
    target = $scope.ActiveJob.profile[profile].target.length;
    $scope.ActiveJob.profile[profile].target[target] = $scope.TargetDataDefault();
    $scope.Target.Active = target.toString();
    $scope.AssetsPreviewBuild($scope.ActiveJob);
    $log.debug('TargetAdd: ActiveJob Targets: ', $scope.ActiveJob.profile[profile].target);
  }


  // Delete a target in Edit dialog
  $scope.TargetDelete = function(profile, target) {
    target = parseInt(target);
    $scope.ActiveJob.profile[profile].target.splice(target, 1);
    if (target == $scope.ActiveJob.profile[profile].target.length) {
      target = target - 1;
    }
    $scope.Target.DeleteConfirm = false;
    $scope.Target.Active = target.toString();
    $scope.AssetsPreviewBuild($scope.ActiveJob);
    $log.debug('TargetDelete: ActiveJob Targets: ', $scope.ActiveJob.profile[profile].target);
  }


  // Change selected HLS segment format type (timestamp/sequence)
  $scope.TargetHLSSegmentFormatChange = function(target) {
    if (target.hls_seg_format == 'Timestamp') {
      target.hls_seg_name = '%Y%m%d%H%M%S';
    } else {
      target.hls_seg_name = '%03d';
    }
  }


  // Target type options init
  $scope.TargetTypeSelect = function(Profile, Target) {
    var TargetData = $scope.ActiveJob.profile[Profile].target[Target];
    if (TargetData.target_type == 'Device') {
      $scope.MediaSourceLocal.Devices.length ? TargetData.device_name = $scope.MediaSourceLocal.Devices[0].name : null;
    }
    $log.debug('TargetTypeSelect: ', TargetData);
    $scope.ActiveJob.profile[Profile].target[Target] = TargetData;
  }


  // Activate first protocol of selected Server
  $scope.TargetServerSelect = function(Profile, Target) {
    $scope.ActiveJob.profile[Profile].target[Target].stream_type = $scope.Servers.List[$scope.ActiveJob.profile[Profile].target[Target].stream_srv].features[0].name;
    $scope.AssetsPreviewBuild($scope.ActiveJob);
    $log.debug('TargetServerSelect: Server Features: ', $scope.Servers.List[$scope.ActiveJob.profile[Profile].target[Target].stream_srv].features);
  }


  // Return preset data by its name and type
  $scope.PresetDataParse = function(Presets) {
    $scope.Presets = Presets;
    $scope.Presets.data = [
      { name: 'copy', alias: 'Stream copy' },
//      { name: 'scte35', alias: 'SCTE-35' }
    ];
    PresetTypes = [
      { FilterName: 'vpreset', Value: 'video' },
      { FilterName: 'apreset', Value: 'audio' }
    ];
    for (PresetType in PresetTypes) {
      PresetType = PresetTypes[PresetType];
      for (Preset in Presets[PresetType.Value]) {
        Preset = Presets[PresetType.Value][Preset];
        $scope.FilterList[PresetType.FilterName].options.push({ value: Preset.filename, alias: Preset.name });
      }
    }
  }

  // Return preset data by its name and type
  $scope.PresetDataGet = function(preset, type) {
    for (p in $scope.Presets[type]) {
      if ($scope.Presets[type][p].filename == preset) {
        return $scope.Presets[type][p];
      }
    }
    return null;
  }


  // Check if Profile has GPU options
  $scope.vPresetGPUCheck = function(vcodec) {
    return vcodec.includes('nvenc');
  }


  // TODO: Simplify ABR meta parse
  $scope.PresetSelect = function(PresetType) {
    var vPresetData = null;
    var aPresetData = null;
    if ($scope.Profile.Options[$scope.Profile.Active].EncoderActive.video) {
      var vPresetName = $scope.ActiveJob.profile[$scope.Profile.Active].vpreset;
      vPresetData = $scope.PresetDataGet(vPresetName, 'video');
      if (vPresetName == 'Copy') {
        $scope.ActiveJob.profile[$scope.Profile.Active].venc_psize = '';
        $scope.ActiveJob.profile[$scope.Profile.Active].venc_di = null;
        $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_resolution = null;
        $scope.Profile.Options[$scope.Profile.Active].vFilters.Scale.Value = '';
      } else {
        $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_resolution = $scope.ActiveJob.profile[$scope.Profile.Active].venc_psize;
        $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_bandwidth = vPresetData.vbitrate * 1024;
      }
      if (vPresetData) {
        // Check if profile is GPU powered
        var isGPUProfile = $scope.vPresetGPUCheck(vPresetData.vcodec);
        $scope.Profile.Options[$scope.Profile.Active].isGPUProfile = isGPUProfile;
        // Set GPU auto select
        if (isGPUProfile) {
          $scope.ActiveJob.profile[$scope.Profile.Active].nvenc_gpu = 'auto';
        } else {
        // Set Job as not GPU powered
          $scope.ActiveJob.profile[$scope.Profile.Active].nvenc_gpu = 'none';
        }
      }
    } else {
      $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_bandwidth = null;
      $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_resolution = null;
      $log.debug('PresetSelect: vPresetData: ', vPresetData);
    }
    if ($scope.Profile.Options[$scope.Profile.Active].EncoderActive.audio) {
      var aPresetName = $scope.ActiveJob.profile[$scope.Profile.Active].apreset;
      aPresetData = $scope.PresetDataGet(aPresetName, 'audio');
      $log.debug('PresetSelect: aPresetData: ', aPresetData);
    }
    $scope.ActiveJob.profile[$scope.Profile.Active].target[$scope.Target.Active].hls_abr_codecs = $scope.ABRMetadataCodecs(vPresetData, aPresetData);
    $scope.ABRMetadataBuild($scope.ActiveJob);
  }


  $scope.ABRMetadataCodecs = function(vPresetData, aPresetData) {
  //  $log.debug('PresetData: ', vPresetData, aPresetData);
    var vCodec = '';
    if (vPresetData) {
      if (vPresetData.vcodec == 'libx264' || vPresetData.vcodec == 'h264_nvenc') {
        vCodec = 'avc1.4d401f';
      }
    }
    var aCodec = '';
    if (aPresetData) {
      if (aPresetData.acodec == 'libfdk_aac') {
        aCodec = 'mp4a.40.2';
      }
    }
    CodecsJoin = (vCodec || '') + ((vCodec && aCodec) ? ', ' : '') + (aCodec || '');
    return CodecsJoin;
  }


  // metadata assets defaults
  $scope.MetadataAssetsDefault = function() {
    return { ABR: [] , DRM: [] };
  }


  // Select manifest to include in ABR assets
  $scope.ABRManifestSelect = function(Asset) {
    $scope.ActiveJob.profile[Asset.Profile].target[Asset.Target].hls_abr_asset = !$scope.ActiveJob.profile[Asset.Profile].target[Asset.Target].hls_abr_asset;
  }


  // Update ABR metadata assets with ActiveJob data
  $scope.ABRMetadataParse = function(ActiveJob, Profile, Target) {
    var TargetData = ActiveJob.profile[Profile].target[Target];
    if (TargetData.stream_type == 'HLS') {
      var Base = ActiveJob.job_data.hls_abr_basename;
      var Manifest = '/' + ((ActiveJob.job_data.hls_abr_active && Base) ? Base + '/' : '') + (TargetData.stream_name || '<stream_name>') + '/' + (TargetData.hls_list_name || '<hls_manifest_name>') + '.m3u8';
      $scope.MetadataAssets.DRM.push({ Profile: Profile, Target: Target, Manifest: Manifest });
      if (TargetData.stream_srv == ActiveJob.job_data.hls_abr_server) {
        $scope.MetadataAssets.ABR.push({ Profile: Profile, Target: Target, Manifest: Manifest });
      }
    }
  }


  // TODO: join ABRMetadataBuild and AssetsPreviewBuild
  // Build ActiveJob ABR assets
  $scope.ABRMetadataBuild = function(ActiveJob) {
    $scope.MetadataAssets = $scope.MetadataAssetsDefault();
    Profiles = ActiveJob.profile;
    for (Profile in Profiles) {
      for (Target in Profiles[Profile].target) {
        $scope.ABRMetadataParse(ActiveJob, Profile, Target);
      }
    }
    $log.debug('ABRMetadataBuild: MetadataAssets: ', $scope.MetadataAssets);
  }


  // Dynamic build of ABR Manifest URL
  $scope.ABRPreviewBuild = function(ActiveJob) {
    $scope.PreviewABR = Tools.PreviewABR(ActiveJob, $scope.Servers.List);
    $log.debug('ABRPreviewBuild: PreviewABR: ', $scope.PreviewABR);
  }


  // Select manifest to include in DRM assets
  $scope.DRMManifestSelect = function(Asset) {
    $scope.ActiveJob.profile[Asset.Profile].target[Asset.Target].hls_drm_asset = !$scope.ActiveJob.profile[Asset.Profile].target[Asset.Target].hls_drm_asset;
  }


  // Generate DRM Key/IV
  $scope.DRMKeygen = function(Mode) {
    $http.post('/api/v1/tools/drm_keygen')
    .then(
      function(success) {
        $log.debug('DRMKeygen response: ', success);
        var data = success.data;
        if (Mode == 'Key' ) { $scope.ActiveJob.job_data.hls_drm_key = data.key; }
        if (Mode == 'IV' ) { $scope.ActiveJob.job_data.hls_drm_key_iv = data.key; }
      },
      function(error) {
        $log.error('DRMKeygen response: ', error);
        Alerts.Add('jobs', 'danger', 'DRMKeygen: ' + error.statusText);
      }
    );
  }


  // Dynamic build all Targets previews and ABR metadata assets
  $scope.AssetsPreviewBuild = function(ActiveJob) {
    $scope.PreviewURLDynamic = Tools.PreviewURL(ActiveJob, 'tree', 'dynamic', $scope.Servers.List);
    $scope.ABRMetadataBuild($scope.ActiveJob);
    $scope.ABRPreviewBuild($scope.ActiveJob);
    $log.debug('AssetsPreviewBuild: PreviewURLDynamic: ', $scope.PreviewURLDynamic);
  }


  // JSON keys delete
  $scope.DeleteJSONKeys = function(json_data, keys) {
    for (k in keys) {
      delete json_data[keys[k]];
    }
    return json_data;
  }


  // Delete unwanted JSON key(s) from Job data asset
  $scope.JobDataClean = function(job_data, keys) {
    job_data.job_data = $scope.DeleteJSONKeys(job_data.job_data, keys);
    var profiles = job_data.profile;
    for (p in profiles) {
      profiles[p] = $scope.DeleteJSONKeys(profiles[p], keys);
      var targets = profiles[p].target;
      for (t in targets) {
        targets[t] = $scope.DeleteJSONKeys(targets[t], keys);
      }
      profiles[p].target = targets;
    }
    job_data.profile = profiles;
    return job_data;
  }


  // Init Job add data
  $scope.JobAddInit = function() {
    // AV presets get
    AVPresets.Get()
    .then(
      function(PresetData) {
        $scope.PresetDataParse(PresetData);
        $scope.EditMode = 'add';
        // Set Job data default values
        $scope.ActiveJob = $scope.JobDataDefault();
        // Reset MediaInfo dialog
        $scope.MediaInfoReset();
        // Set Job dialog default values
        $scope.JobOptionsDefault();
        // Add default Profile options value
        $scope.Profile.Options.push($scope.ProfileOptionsDefault());
        // Get local media list. Apply Source init mapping.
        $scope.GetMediaSourceLocal($scope.ActiveJob);
        // ABR init
        $scope.MetadataAssets = $scope.MetadataAssetsDefault();
        // Getting Presets data
        $scope.AssetsPreviewBuild($scope.ActiveJob);
        $scope.ChapterTitle = 'New Job';
        // Edit dialog show
        $scope.EditShow = true;
        $scope.StopPolls();
        $log.debug('JobAddInit: ActiveJob: ', $scope.ActiveJob);
      },
      function(error) {
        Alerts.Add('jobs', 'danger', 'AV Presets: ' + error.statusText);
      }
    );
  }


  // Submit Job add data
  $scope.JobAdd = function() {
    $scope.SubmitBlock = true;
    var NewJobData = angular.copy($scope.ActiveJob);
    NewJobData = $scope.JobDataClean(NewJobData, [ 'id', 'start_time', 'uptime', 'retries', 'run_status', 'sys_stats' ]);
    NewJobData.job_start = $scope.EditSettings.JobStart;
    $log.debug('JobAdd: NewJobData: ', NewJobData);
    $http.post('/api/v1/job/add', NewJobData)
    .then(
      function(success) {
        $log.debug('JobAdd response: ', success);
        if ($scope.EditSettings.KeepOpen) {
          $scope.EditSettings.SaveData ? null : $scope.JobAddInit();
          $scope.ActiveJob.job_data.sid += 1;
        } else {
          $scope.JobEditCancel();
        }
        Alerts.Add('jobs', 'success', 'Job add:' + success.statusText);
      },
      function(error) {
        $log.error('JobAdd response: ', error);
        Alerts.Add('jobs', 'danger', 'Job add:' + error.statusText);
      }
    )
    .finally(function() {
      $scope.SubmitBlock = false;
      $scope.StartPolls();
    });
  }


  // Init Job update data
  $scope.JobUpdateInit = function(job_index, duplicate) {
    // AV presets get
    AVPresets.Get()
    .then(
      function(PresetData) {
        // Set active Job for editing
        $scope.ActiveJob = angular.copy($scope.Jobs.List[job_index]);
        $scope.DeleteJSONKeys($scope.ActiveJob.job_data, [ 'retries', 'run_status' ]);
        // Selected Job copy for compare values
        $scope.ActiveJobCopy = angular.copy($scope.ActiveJob);
        // Set current Job index (Prev/Next jobs selection in navbar)
        $scope.CurrentIndex = job_index;
        if (duplicate) {
          $scope.EditMode = 'add';
          $scope.ChapterTitle = 'Duplicate Job';
          $scope.ActiveJob.job_data.sid = $scope.JobLastUserID() + 1;
        } else {
          $scope.EditMode = 'update';
          $scope.ChapterTitle = 'Edit Job';
        }
        // Reset MediaInfo dialog
        $scope.MediaInfoReset();
        // Set Job dialog default values
        $scope.JobOptionsDefault();
        // Get local media list and apply Source mapping
        $scope.GetMediaSourceLocal($scope.ActiveJob);
        // ABR init
        $scope.MetadataAssets = $scope.MetadataAssetsDefault();
        $scope.ProfileOptionsInit($scope.ActiveJob);
        $scope.AssetsPreviewBuild($scope.ActiveJob);
        // Edit dialog show
        $scope.EditShow = true;
        $scope.StopPolls();
        $log.debug('JobUpdateInit: ActiveJob: ', $scope.ActiveJob);
      },
      function(error) {
        Alerts.Add('jobs', 'danger', 'AV Presets: ' + error.statusText);
      }
    );
  }


  // Submit Job update data
  $scope.JobUpdate = function() {
    $scope.SubmitBlock = true;
    var UpdateJobData = angular.copy($scope.ActiveJob);
    // TODO: Move restart_required to backend, make JSON key optional
    UpdateJobData.restart_required = Tools.CompareObj(false, $scope.ActiveJobCopy, $scope.ActiveJob, [ 'sid', 'job_name', 'source_main_bak_rr', 'hls_drm_key_type', 'hls_drm_key_user', 'hls_drm_key_password', 'hls_drm_key', 'hls_drm_key_url', 'hls_drm_key_iv' ]);
    $log.debug('JobUpdate: ', UpdateJobData);
    $http.post('/api/v1/job/update', UpdateJobData)
    .then(
      function(success) {
        $log.debug('JobUpdate response:', success);
        $scope.EditSettings.KeepOpen ? null : $scope.JobEditCancel();
        $scope.JobListFilterChange();
        Alerts.Add('jobs', 'success', 'Job update: ' + success.statusText);
      },
      function(error) {
        $log.error('JobUpdate response:', error);
        Alerts.Add('jobs', 'danger', 'Job update: ' + error.statusText);
      }
    )
    .finally(function() {
      $scope.SubmitBlock = false;
      $scope.StartPolls();
    });
  }


  // Loads next job in editor
  $scope.JobEditNext = function() {
    if ($scope.CurrentIndex == $scope.Jobs.List.length - 1) {
      $scope.CurrentIndex = 0;
    } else {
      $scope.CurrentIndex += 1;
    }
    $scope.JobUpdateInit($scope.CurrentIndex, false);
    $log.debug('JobEditNext key: ', $scope.CurrentIndex);
  }


  // Loads previous job in editor
  $scope.JobEditPrev = function() {
    if ($scope.CurrentIndex == 0) {
      $scope.CurrentIndex = $scope.Jobs.List.length - 1;
    } else {
      $scope.CurrentIndex -= 1;
    }
    $scope.JobUpdateInit($scope.CurrentIndex, false);
    $log.debug('JobEditNext key: ', $scope.CurrentIndex);
  }


  // Edit dialog hide
  $scope.JobEditCancel = function() {
    $scope.ChapterTitle = 'Jobs';
    $scope.EditShow = false;
    $scope.EditSettings = { JobStart: false, SaveData: false, KeepOpen: false };
    $scope.StartPolls();
  }


  // Job data submit (Add/Update)
  $scope.JobDataSubmit = function(mode) {
    if (mode == 'add') { $scope.JobAdd(); }
    if (mode == 'update') { $scope.JobUpdate(); }
  }


  // Job pre-actions decorator
  $scope.JobPreAction = function(job_id, api) {
    var CheckPassed = false;
    var StatusMsg = ' ALL';
    $scope.Actions.JobBusy = {};
    if ($scope.Jobs.Total > 0) {
      if (job_id.length) {
        job_id.forEach(function(id) { $scope.Actions.JobBusy[id] = true; });
        StatusMsg = '';
      }
      CheckPassed = true;
    } else {
      Alerts.Add('jobs', 'danger', 'Job ' + api + ': No job(s) to process');
    }
    return { Passed: CheckPassed, Msg: StatusMsg };
  }


  // Job post-actions decorator
  $scope.JobPostAction = function(job_id) {
    job_id.length ? job_id.forEach(function(id) { $scope.Actions.JobBusy[id] = false; }) : null;
  }


  // Start/Stop a job
  $scope.JobStartStop = function(job_id, api) {
    $log.debug('JobStartStop API:', api, ', JobID:', job_id);
    var StartupCheck = $scope.JobPreAction(job_id, api);
    if (StartupCheck.Passed) {
      $http.post('/api/v1/job/' + api, { 'id': job_id })
      .then(
        function(success) {
          $log.debug('JobStartStop response:', success);
          Alerts.Add('jobs', 'success', 'Job ' + api + StartupCheck.Msg + ': ' + success.statusText);
        },
        function(error) {
          $log.error('JobStartStop response:', error);
          Alerts.Add('jobs', 'danger', 'Job ' + api + StartupCheck.Msg + ': '+ error.statusText);
        }
      )
      .finally(function() { $scope.JobPostAction(job_id); });
    }
  }


  // Delete dialog init
  $scope.JobDeleteInit = function(job_id) {
    $scope.Actions.JobDelete[job_id] = true;
    $scope.StopPolls();
  }


  // Delete dialog cancel
  $scope.JobDeleteCancel = function(job_id) {
    $scope.Actions.JobDelete[job_id] = false;
    $scope.StartPolls();
  }


  // Delete a job
  $scope.JobDelete = function(job_id) {
    $log.debug('JobDelete JobID: ', job_id);
    var StartupCheck = $scope.JobPreAction(job_id, 'delete');
    if (StartupCheck.Passed) {
      $http.post('/api/v1/job/delete', { 'id': job_id })
      .then(
        function(success) {
          $log.debug('JobDelete response:', success);
          Alerts.Add('jobs', 'success', 'Job delete ' + StartupCheck.Msg + ': ' + success.statusText);
        },
        function(error) {
          $log.error('JobDelete response:', error);
          Alerts.Add('jobs', 'danger', 'Job delete'  + StartupCheck.Msg + ': ' + error.statusText);
        }
      )
      .finally(function() {
        $scope.JobPostAction(job_id);
        $scope.JobDeleteCancel(job_id);
      });
    }
  }


  // Run status info display
  $scope.JobRunStatus = function(run_status) {
    if (run_status == 'ERR_SRC') { run_status = 'Source error'; }
    if (run_status == 'ERR_ENC') { run_status = 'Encode error'; }
    return run_status;
  }


  // Preview modal window
  $scope.JobPreview = function(Job) {
    $uibModal.open({
      animation: true,
      size: 'lg',
      templateUrl: 'html/player.html',
      controller: 'PlayerController',
      resolve: {
        JobData: function() { return Job; }
      }
    });
  }


  // Display log modal
  $scope.JobLogShow = function(Job) {
    var LogModal = $uibModal.open({
      animation: true,
      templateUrl: 'html/log.html',
      controller: 'LogController',
      windowClass: 'app-modal modal-btns',
      resolve: {
        JobData: function() { return Job; }
      }
    });
    LogModal.result.catch(function() { LogModal.close(); });
  }


  // Clear hash when filter values are changing
  $scope.JobListFilterChange = function() {
    //$scope.Jobs.Hash = null;
    LSM.Save({ GUI: $rootScope.GUI });
  }


  // Limits an input for per page input dialog (min = 1)
  $scope.JobListPerPageReset = function() {
    if (!$rootScope.GUI.Jobs.PerPage) { $rootScope.GUI.Jobs.PerPage = 1; }
    LSM.Save({ GUI: $rootScope.GUI });
  }


  // Sort-by criteria filter (ascending or descending)
  $scope.JobListRunSortBy = function(item) {
    $rootScope.GUI.Jobs.SortByOrder == 'asc'? $rootScope.GUI.Jobs.SortByOrder = 'desc' : $rootScope.GUI.Jobs.SortByOrder = 'asc';
    $scope.JobListFilterChange();
  }


  $scope.JobFiltersShow = function() {
    $rootScope.GUI.Jobs.Filters.Show = !$rootScope.GUI.Jobs.Filters.Show;
    LSM.Save({ GUI: $rootScope.GUI });
  }


  // Reset filter value on select
  // This will clean current filter when user choose another one
  $scope.JobListFilterSelect = function(job_filter) {
    job_filter.value = null;
    $scope.JobListFilterChange();
  }


  // Apply active filtering value
  $scope.JobListQuickFilter = function(field, value) {
    $rootScope.GUI.Jobs.Filters.Quick[value] = !$rootScope.GUI.Jobs.Filters.Quick[value];
    // Add new fast filter
    if ($rootScope.GUI.Jobs.Filters.Quick[value]) {
      if ($rootScope.GUI.Jobs.Filters.List[0].value == null) {
        $rootScope.GUI.Jobs.Filters.List = [ { field: field, value: value, type: 'or' } ];
      } else {
        $rootScope.GUI.Jobs.Filters.List.push({ field: field, value: value, type: 'or' });
      }
    } else {
    // Find and remove fast filter(s)
      for (f in $rootScope.GUI.Jobs.Filters.List) {
        if ($rootScope.GUI.Jobs.Filters.List[f].field == field && $rootScope.GUI.Jobs.Filters.List[f].value == value) {
          if ($rootScope.GUI.Jobs.Filters.List.length == 1) {
            $scope.JobListAddFilter()
          }
          $rootScope.GUI.Jobs.Filters.List.splice(f, 1);
        }
      }
    }
    $scope.JobListFilterChange();
  }


  // Add new filter
  $scope.JobListAddFilter = function() {
    $rootScope.GUI.Jobs.Filters.List.push({ field: 'sid', value: null, type: 'or' });
    $scope.JobListFilterChange();
  }


  // Delete new filter
  $scope.JobListDeleteFilter = function(index, JobFilter) {
    $log.debug('JobListDeleteFilter: index: ', index, ', JobFilter: ', JobFilter);
    $rootScope.GUI.Jobs.Filters.Quick[JobFilter.value] = !$rootScope.GUI.Jobs.Filters.Quick[JobFilter.value];
    if (index == 0 && $rootScope.GUI.Jobs.Filters.List.length == 1) {
      $scope.JobListFiltersDefault();
    } else {
      $rootScope.GUI.Jobs.Filters.List.splice(index, 1);
    }
    $scope.JobListFilterChange();
  }


  // Reset all filter default values
  $scope.JobListFiltersDefault = function() {
    $rootScope.GUI.Jobs.Filters.List = [ { field: 'sid', value: null, type: 'or' } ];
    $rootScope.GUI.Jobs.Filters.Quick = { 'OK': false, 'ERR': false, 'UPD': false, 'OFF': false };
    $scope.JobListFilterChange();
  }


  // Job list request. Filter(s) and hash are optional.
  $scope.JobListGet = function() {
    var JobListRequest = {
      hash: $scope.Jobs.Hash,
//      hash: null,
      filters: $rootScope.GUI.Jobs.Filters.List,
      sort_by: $rootScope.GUI.Jobs.SortBy,
      sort_by_order: $rootScope.GUI.Jobs.SortByOrder,
      per_page: $rootScope.GUI.Jobs.PerPage,
      act_page: $rootScope.GUI.Jobs.ActPage
    };
    $log.debug('JobListGet: JobListRequest: ', JobListRequest);
    $http.post('/api/v1/job/list', JobListRequest)
    .then(
      function(success) {
        $log.debug('JobListGet response: ', success);
        var data = success.data;
        // Check if DB data delivered
        if ('jobs_total' in data) {
          // Total Jobs counter
          $scope.Jobs.Total = data.jobs_total;
          // Check if DB filtering was applied
          $scope.isFiltered = data.filtered;
          // Per job variables: stats, screenshot, uptime, etc
          $scope.Jobs.Var = data.var;
          if (data.jobs_total > 0) {
            if ($scope.Jobs.Hash == data.hash) {
              $log.debug('JobListGet: Job list is up to date');
            } else {
              //if (data.job_list.length) {
                $log.debug('JobListGet: Job list update required');
                $scope.Jobs.Hash = data.hash;
                $scope.Jobs.List = data.job_list;
              //}
            }
          } else {
            $scope.Jobs.Hash = data.hash;
            $scope.Jobs.List = data.job_list;
            $log.debug('JobListGet: JobsList is empty');
          }
          $scope.Jobs.Filtered = $scope.Jobs.List.length;
          $scope.ContentLoaded = true;
        } else {
          $scope.ContentLoaded = false;
        }
        $log.debug('JobListGet: Jobs: ', $scope.Jobs);
      },
      function(error) {
        $log.error('JobListGet response:', error);
        $scope.Jobs = { List: [], Hash: null, Total: 0 };
        $scope.ContentLoaded = false;
      }
    );
  }


  // Server list request. Hash is optional.
  $scope.ServerListGet = function() {
    ServerList.Get($scope.Servers)
    .then(
      function(servers) {
        $scope.Servers = servers;
        if ($scope.Servers.Updated) {
          $scope.Servers.List = $scope.ServerListParse($scope.Servers.List);
        }
        $log.debug('ServerListGet: Servers: ', $scope.Servers);
      },
      function(error) {
        //Alerts.Add('jobs', 'danger', 'ServerList: ' + error.statusText);
      }
    );
  }


  // Replace 'localhost' to actual DNS/IP data
  $scope.ServerListParse = function(server_list) {
    var ServerListJSON = {};
    for (srv in server_list) {
      var server = server_list[srv];
      $scope.FilterList.stream_srv.options.push({
        value: server.id,
        alias: server.name + ' (' + server.ip + ')'
      });
      if (server.ip == 'localhost') {
        server.ip = Tools.GetReferrer().hostname;
        for (f in server.features) {
          server.features[f].url = Tools.LocalhostIPReplace(server.features[f].url);
        }
      }
      ServerListJSON[server.id] = server;
    }
    return ServerListJSON;
  }


  // Start poll(s)
  $scope.StartPolls = function() {
    $scope.StopPolls();
    Polls.JobList.Checker = $interval(function() {
      if ($rootScope.CurrentUser.Name) {
        $scope.ServerListGet();
        $scope.JobListGet();
      }
    }, Polls.JobList.Timer);
    $log.debug('JobList poll started');
  }


  // Stop poll(s)
  $scope.StopPolls = function() {
    $interval.cancel(Polls.JobList.Checker);
    $log.debug('JobList poll terminated');
  }


  // Reset controller on view change
  $scope.$on('$destroy', function() {
    $scope.StopPolls();
    $scope.ContentLoaded = false;
  });


  // First load controller init
  $scope.ControllerInit = function() {
//    if ($rootScope.CurrentUser.Name) {
      //
      Stats.Get()
      .then(
        function(success) {
          $scope.GPUInit(success.data.hardware.gpu);
        },
        function(error) {
          $scope.GPUInit();
        }
      )
      .finally(function() {
        // AV presets get
        AVPresets.Get()
        .then(
          function(PresetData) {
            $scope.PresetDataParse(PresetData);
          },
          function(error) {
            Alerts.Add('jobs', 'danger', 'AV Presets: ' + error.statusText);
          }
        )
        .finally(function() {
          $scope.StartPolls();
        });
      });
      $log.debug('JobsController initialized');
//    }
  }

  $scope.ControllerInit();

});
