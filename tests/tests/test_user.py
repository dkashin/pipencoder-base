
User = [
  {
    'name': 'UserAdd',
    'url': 'user/add',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'username': 'test_user',
          'password': 'test_pwd',
          'alias': None,
          'admin': True,
          'su': False,
        },
        'result': '200 OK'
      },
      {
        'name': 'User name exists',
        'payload': {
          'username': 'test_user',
          'password': 'test_pwd'
        },
        'result': '400 User name has already taken'
      },
      {
        'name': 'JSON key error',
        'payload': {
          'key_error': 'value_error'
        },
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'UserList',
    'url': 'user/list',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'UserUpdate',
    'url': 'user/update',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'id': None,
          'username': 'test_user',
          'password': 'new_pwd',
          'admin': False
        },
        'result': '200 OK'
      },
      {
        'name': 'User name exists',
        'payload': {
          'id': None,
          'username': 'admin',
          'admin': False
        },
        'result': '400 User name has already taken'
      },
      {
        'name': 'User ID error',
        'payload': { 'id': 'value_error' },
        'result': '400 User is not found'
      },
      {
        'name': 'JSON key error',
        'payload': { 'key_error': 'value_error' },
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'UserDelete',
    'url': 'user/delete',
    'cases': [
      {
        'name': 'Regular',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'User ID error',
        'payload': { 'id': 'value_error' },
        'result': '400 User is not found'
      },
      {
        'name': 'JSON key error',
        'payload': { 'key_error': 'value_error' },
        'result': '400 Required key(s)'
      }
    ]
  }
]
