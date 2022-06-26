
Login = [
  {
    'name': 'AuthLogin',
    'url': 'login',
    'cases': [
      {
        'name': 'Username error',
        'payload': {
          'username': 'fake_user_name',
          'password': 'fake_password'
        },
        'result': '400 Invalid username and/or password'
      },
      {
        'name': 'Password error',
        'payload': {
          'username': 'admin',
          'password': 'fake_password'
        },
        'result': '400 Invalid username and/or password'
      },
      {
        'name': 'API key action error',
        'payload': {
          'username': 'admin',
          'password': 'admin',
          'api_key_options': {
            'action': 'error_action',
            'key_ttl': 3600
          }
        },
        'result': '200 OK'
      },
      {
        'name': 'API key JSON error',
        'payload': {
          'username': 'admin',
          'password': 'admin',
          'api_key_options': { 'key_error': 'value_error' }
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': { 'key_error': 'value_error' },
        'result': '400 Required key(s)'
      },
      {
        'name': 'Regular',
        'payload': {
          'username': 'admin',
          'password': 'admin',
          'api_key_options': {
            'action': 'create',
            'key_ttl': 3600
          }
        },
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'AuthLoggedUser',
    'url': 'logged_user',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  }
]


Logout = [
  {
    'name': 'AuthLogout',
    'url': 'logout',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  }
]
