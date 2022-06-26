
// Alerts
app.factory('Alerts', function() {

  var Alerts = {};
  var Queue = [];

  Alerts.Queue = Queue;

  Alerts.Add = function (action, type, msg) {
    Queue.push({ 'action': action, 'type': type, 'msg': msg });
  };

  Alerts.Close = function(index) {
    Queue.splice(index, 1);
  };

  return Alerts;

});


// Authorize
app.factory('Auth', function($q, $http, $log, $rootScope) {

  var Auth = {};
  var NullUser = { Name: null, isAdmin: false };

  Auth.NullUser = function() { return NullUser; };

  Auth.Login = function(AuthData) {
    var deferred = $q.defer();
    $http.post('/api/v1/login', AuthData)
    .then(
      function(success) {
        $log.debug('Login response:', success);
        $rootScope.CurrentUser = { Name: AuthData.username, isAdmin: success.data.admin };
        deferred.resolve(success);
      },
      function(error) {
        $log.error('Login response:', error);
        $rootScope.CurrentUser = NullUser;
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  Auth.Logout = function() {
    var deferred = $q.defer();
    $http.post('/api/v1/logout')
    .then(
      function(success) {
        $log.debug('Logout response:', success);
        $rootScope.CurrentUser = NullUser;
        deferred.resolve(success);
      },
      function(error) {
        $log.error('Logout response:', error);
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  Auth.GetLoggedUser = function() {
    var deferred = $q.defer();
    $http.post('/api/v1/logged_user')
    .then(
      function(success) {
        $log.debug('GetLoggedUser response:', success);
        var logged_user = success.data.logged_user;
          $rootScope.CurrentUser = logged_user ? { Name: logged_user.username, isAdmin: logged_user.admin } : NullUser;
        deferred.resolve(success);
      },
      function(error) {
        //$log.error('GetLoggedUser response:', error);
        $rootScope.CurrentUser = NullUser;
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  return Auth;

});


app.factory('Interceptors', function($rootScope, $q, $location, $injector, $log) {
  return {
    responseError: function responseError(rejection) {
      // Auth 401 handler
      //$log.debug('rejection:', rejection);
      if (rejection.status === 401 &&
          !rejection.config.url.includes('/login') &&
          !rejection.config.url.includes('/node/activate'))
      {
        var AuthService = $injector.get('Auth');
        // Reset current user and activate lock screen
        if ($rootScope.CurrentUser) {
          $rootScope.CurrentUser = AuthService.NullUser;
        } else {
          $location.path('/login');
        }
      }
      return $q.reject(rejection);
    }
  };
});


// Node services
app.factory('Node', function($q, $http, $log, $rootScope) {

  var Node = {};

  Node.Service = function(API, NodeData) {
    var deferred = $q.defer();
    $http.post('/api/v1/node/' + API, NodeData)
    .then(
      function(success) {
        $log.debug('Node', API, 'response:', success);
        if (API == 'auth') {
          Node.Service('activate')
          .then(
            function(success) { deferred.resolve(success); },
            function(error) { deferred.reject(error); }
          );
        }
        else {
          var data = success.data;
          if (API == 'activate') {
            $rootScope.LicenseInfo = data.node_data;
            $rootScope.LicenseInfo.status = success.statusText;
            deferred.resolve(success);
          }
          if (API == 'deactivate') {
            $rootScope.LicenseInfo = null;
            deferred.resolve(success);
          }
        }
        $log.debug('LicenseInfo: ', $rootScope.LicenseInfo);
      },
      function(error) {
        $log.error('Node', API, 'response:', error);
        var data = error.data;
        if (data.node_data) {
          $rootScope.LicenseInfo = data.node_data;
          $rootScope.LicenseInfo.status = error.statusText;
        } else {
          $rootScope.LicenseInfo = null;
        }
        $log.debug('LicenseInfo: ', $rootScope.LicenseInfo);
        deferred.reject(error);
      }
    );
    return deferred.promise;
  }

  return Node;

});

// Local storage manager
app.factory('LSM', function($rootScope, $log) {

  var LSM = {};

  LSM.Load = function(Value) {
    var UserLSData = null;
    if ($rootScope.CurrentUser.Name in localStorage) {
      UserLSData = JSON.parse(localStorage[$rootScope.CurrentUser.Name]);
      Value ? UserLSData = UserLSData[Value] : null;
      $log.debug('LSM.Load:', UserLSData);
    } else {
      $log.debug('LSM.Load: User has no saved settings');
    }
    return UserLSData;
  };

  LSM.Save = function(Data) {
    var UserLSData = JSON.parse(localStorage[$rootScope.CurrentUser.Name] || '{}');
    UserLSData = Object.assign({}, UserLSData, Data);
    $log.debug('LSM.Save:', UserLSData);
    localStorage[$rootScope.CurrentUser.Name] = JSON.stringify(UserLSData);
  };

  return LSM;

});


// Filters
app.factory('Filters', function() {

  var Filters = {};
  var FiltersData;
  var Logic = [
    { 'alias': 'AND', 'value': 'and' },
    { 'alias': 'OR', 'value': 'or' }
  ];

  Filters.Default = function() {
    return angular.copy(FiltersData.Default);
  };

  Filters.Init = function(Data) {
    FiltersData = Data;
  };

  Filters.Data = function() {
    return FiltersData;
  };

  Filters.Logic = function() {
    return Logic;
  };

  Filters.Add = function() {
    FiltersData.Active.push(Default());
  };

  Filters.Delete = function(index, active_filter) {
    if (active_filter.value in FiltersData.Quick) {
      FiltersData.Quick[active_filter.value] = !FiltersData.Quick[active_filter.value];
    }
    if (index == 0 && FiltersData.Active.length <= 1) {
      FiltersData.Active = [ Default() ];
    } else {
      FiltersData.Active.splice(index, 1);
    }
  };

  Filters.Change = function() {};

  Filters.Show = function() {
    FiltersData.Show = !FiltersData.Show;
  };

  Filters.Reset = function(active_filter) {
    active_filter.value = null;
  };

  // Apply filter preset (quick filter)
  Filters.Quick = function(field, value, type) {
    FiltersData.Quick[value] = !FiltersData.Quick[value];
    // Add new filter
    if (FiltersData.Quick[value]) {
      if (FiltersData.Active[0].value == null) {
        FiltersData.Active = [ Default() ];
        FiltersData.Quick.forEach(function(value, key) { FiltersData.Quick[key] = false; });
      } else {
        FiltersData.Active.push({ field: field, value: value, type: type });
      }
    } else {
    // Find and remove filter
      for (FA in FiltersData.Active) {
        if (FiltersData.Active[FA].field == field && FiltersData.Active[FA].value == value) {
          if (FiltersData.Active.length == 1) { Add() }
          FiltersData.Active.splice(FA, 1);
        }
      }
    }
  };

  return Filters;

});


// System info
app.factory('Stats', function($rootScope, $q, $http, $log) {

  var Stats = {};
  var StatsNull = { cpu: 101, ram: 101, gpu: { dev_count: 0 } };

  Stats.Get = function() {
    var deferred = $q.defer();
    $http.post('/api/v1/tools/system_stats')
    .then(
      function(success) {
        $log.debug('Stats.Get response: ', success);
        var data = success.data || {};
        $rootScope.Stats.Hardware = data.hardware;
        $rootScope.Stats.Jobs = data.jobs;
/*
        // GPU data sample for tests (in case physical GPU is absent):
        $rootScope.Stats.Hardware.gpu = {
          'dev_count': 3,
          'dev_data': [
            { idx: 0, active: true, dev_name: 'GPU Average', dev_opt: { gpu: 50, gram: 50, dec_util: 77, enc_util: 31 }, msg: 'OK' },
            { idx: 1, active: false, dev_name: 'GPU-1', dev_opt: { gpu: 10, gram: 20, dec_util: 0, enc_util: 0 }, msg: 'Device error' },
            { idx: 2, active: true, dev_name: 'GPU-2', dev_opt: { gpu: 30, gram: 70, dec_util: 0, enc_util: 12 }, msg: 'OK' },
          ]
        };
*/
        deferred.resolve(success);
      },
      function(error) {
        $log.error('Stats.Get response: ', error);
        $rootScope.Stats = StatsNull;
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  return Stats;

});


// AV presets
app.factory('AVPresets', function($log, $q, $http) {

  var AVPresets = {};

  AVPresets.Get = function() {
    var deferred = $q.defer();
    $http.post('/api/v1/preset/data')
    .then(
      function(success) {
        $log.debug('AVPresets response:', success);
        var data = success.data;
        deferred.resolve({ video: data.vpresets, audio: data.apresets });
      },
      function(error) {
        $log.error('AVPresets response:', error);
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  return AVPresets;

});


// Servers list
app.factory('ServerList', function($q, $http, $log) {

  var ServerList = {};

  ServerList.Get = function(Servers) {
    var deferred = $q.defer();
    $http.post('/api/v1/server/list', { hash: Servers.Hash })
    .then(
      function(success) {
        $log.debug('ServerList.Get response: ', success);
        var data = success.data;
        Servers.Updated = false;
        if (Servers.Hash == data.hash) {
          $log.debug('ServerList.Get: Servers list is up to date');
        } else {
          Servers.ListCopy = angular.copy(data.server_list);
          Servers.Hash = data.hash;
          Servers.List = data.server_list;
          Servers.Updated = true;
          $log.debug('ServerList.Get: Servers list has been updated');
        }
        deferred.resolve(Servers);
      },
      function(error) {
        $log.error('ServerList.Get response: ', error);
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  return ServerList;

});


// Update
app.factory('AppUpdate', function($rootScope, $q, $http, $log, Events) {

  var AppUpdate = {};

  AppUpdate.Check = function() {
    var deferred = $q.defer();
    $http.post('/api/v1/tools/update_check' )
    .then(
      function(success) {
        var data = success.data;
        $log.debug('SystemUpdateCheck response: ', data);
        if ($rootScope.Stats.Update) {
          if (!$rootScope.Stats.Update.update_allowed) {
            data.update_allowed ? Events.Plus(1) : null;
          }
        } else {
          (Events.Get() == 0 && data.update_allowed) ? Events.Plus(1) : null;
        }
        $rootScope.Stats.Update = data || {};
        deferred.resolve(success);
      },
      function(error) {
        $log.error('SystemUpdateCheck response:', error);
        $rootScope.Stats.Update = error.data || {};
        deferred.reject(error);
      }
    );
    return deferred.promise;
  };

  return AppUpdate;

});


// Events
app.factory('Events', function() {

  var Events = {};
  var Counter = 0;

  Events.Get = function() {
    return Counter;
  };

  Events.Plus = function(value) {
    Counter = Counter + value;
  };

  Events.Minus = function(value) {
    var new_value = Counter - value;
    Counter = new_value > 0 ? new_value : 0;
  };

  Events.Reset = function() {
    Counter = 0;
  };

  return Events;

});


// URL Format
app.factory('Tools', function() {

  var Tools = {};

  // Exception finder
  Tools.ExceptionFind = function(property, exceptions) {
    var result = true;
    for (ex in exceptions) {
      if (property == exceptions[ex]) { result = false; }
    }
    return result;
  };

  // JSON objects compare
  Tools.CompareObj = function(restart, obj1, obj2, exceptions) {
    for (var i in obj2) {
      if (i != '$$hashKey') {
        if (typeof obj2[i] == 'object' && obj1.hasOwnProperty(i)) {
          restart = Tools.CompareObj(restart, obj1[i], obj2[i], exceptions);
        } else {
          if (!obj1 || !obj2 || !obj1.hasOwnProperty(i) || obj2[i] != obj1[i]) {
            if (!restart) { restart = Tools.ExceptionFind(i, exceptions); }
          }
        }
      }
    }
    return restart;
  };

  // Get server IP or Domain name
  Tools.GetReferrer = function() {
    var ref = document.referrer;
    if (window.location === window.top.location ) { ref = window.location.href; }
    var link = document.createElement('a');
    link.setAttribute('href', ref);
    return link;
  };

  // Replace localhost with actual IP/domain
  Tools.LocalhostIPReplace = function(url) {
    if (url) {
      var port = '';
      var ref = Tools.GetReferrer();
      if ((url.search('localhost:') < 0) && ref.port) {
        port = ':' + ref.port;
      }
      return url.replace('://localhost', '://' + ref.hostname + port);
    }
  };

  // Get all preview URL/manifests
  Tools.PreviewABR = function(job_data, servers_list) {
    var url = 'Preview is not available';
    var job_data = job_data.job_data;
    if (Object.keys(servers_list).length && job_data.hls_abr_active) {
      var server = servers_list[job_data.hls_abr_server];
      if (server) {
        for (sf in server.features) {
          feature = server.features[sf];
          if (feature.name == 'HLS') {
            url = feature.url + '/' + (job_data.hls_abr_basename ? job_data.hls_abr_basename + '/' : '') + (job_data.hls_abr_list_name ? job_data.hls_abr_list_name : '<abr_manifest_name>') + '.m3u8';
          }
        }
      }
    }
    preview = { Alias: url, URL: url };
    return preview;
  };

  // Get all preview URL/manifests
  Tools.PreviewConstructor = function(job_data, target, method, servers_list) {
    var url = 'Preview is not available';
    if (method == 'dynamic') {
      var stream_app = target.stream_app || '<stream_app>';
      var stream_name = target.stream_name || '<stream_name>';
      var udp_ip = target.udp_ip || '<udp_ip>';
      var srt_ip = target.srt_ip || '<srt_ip>';
      if (target.target_type == 'Device') {
        url = target.device_name;
      } else {
        if (Object.keys(servers_list).length) {
          var server = servers_list[target.stream_srv];
          if (server) {
            for (sf in server.features) {
              feature = server.features[sf];
              if (feature.name == target.stream_type) {
                if (target.stream_type == 'HLS') {
                  url = feature.url + '/' + ((job_data.hls_abr_basename && job_data.hls_abr_active) ? job_data.hls_abr_basename + '/' : '') + stream_name + '/' + (target.hls_list_name ? target.hls_list_name : '<hls_manifest_name>') + '.m3u8';
                }
                if (target.stream_type == 'RTMP') {
                  url = feature.url + '/' + stream_app + '/' + stream_name;
                }
                if (target.stream_type == 'Smooth') {
                  url = feature.url + '/' + stream_app + '/' + stream_name + '.isml/manifest';
                }
                if (target.stream_type == 'UDP') {
                  url = feature.url + udp_ip + ':' + (target.udp_port ? target.udp_port : '<udp_port>');
                }
                if (target.stream_type == 'SRT') {
                  url = feature.url + srt_ip + ':' + (target.srt_port ? target.srt_port : '<srt_port>');
                }
              }
            }
          }
        }
      }
    }
    if (method == 'static') {
      url = Tools.LocalhostIPReplace(target.preview);
    }
    preview = { alias: url, url: url, stream_type: target.stream_type };
    return preview;
  };

  // Get all preview URL/manifests
  Tools.PreviewURL = function(job_data, listing, method, servers_list, filter) {
    var preview_list = [];
    var all_profiles = job_data.profile;
    var job_data = job_data.job_data;
    for (profile in all_profiles) {
      var preview_targets = [];
      var all_targets = all_profiles[profile].target;
      for (target in all_targets) {
        var target = all_targets[target];
        if (filter) {
          if (target.stream_type == filter) {
            preview = Tools.PreviewConstructor(job_data, target, method, servers_list);
          } else { preview = null; }
        } else {
          preview = Tools.PreviewConstructor(job_data, target, method, servers_list);
        }
        if (listing == 'list') {
          preview ? preview_list.push(preview) : null;
        }
        if (listing == 'tree') {
          preview ? preview_targets.push(preview) : null;
          preview_list[profile] = preview_targets;
        }
      }
    }
    if (listing == 'list' && job_data.hls_abr_active) {
      abr_url = Tools.LocalhostIPReplace(job_data.hls_abr_url);
      preview_list.push({ alias: abr_url, url: abr_url, stream_type: 'HLS' });
    }
    return preview_list;
  };

  return Tools;

});

