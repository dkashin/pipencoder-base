

app.config(['$routeProvider', '$locationProvider', '$logProvider', '$httpProvider', '$injector',
  function($routeProvider, $locationProvider, $logProvider, $httpProvider, $injector) {

    $routeProvider.
      when('/', { redirectTo: '/jobs' }).
      when('/login', { templateUrl: 'html/login.html', controller: 'AuthController' }).
      when('/logout', { controller: 'AuthController' }).
      when('/jobs', { templateUrl: 'html/job_list.html', controller: 'JobsController' }).
      when('/events', { templateUrl: 'html/events.html', controller: 'EventsController' }).
      when('/settings', { templateUrl: 'html/settings.html', controller: 'SettingsController' }).
      otherwise({ redirectTo: '/jobs' });

    $httpProvider.interceptors.push([
      '$injector', function ($injector) { return $injector.get('Interceptors'); }
    ]);

    $locationProvider.html5Mode(true);
    $logProvider.debugEnabled(true);
  }
]);

