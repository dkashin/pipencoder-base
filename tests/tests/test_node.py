
Node = [
  {
    'name': 'NodeAuth',
    'url': 'node/auth',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'account_email': 'uencodemo@ozzmedia.com',
          'account_password': 'uencodemo'
        },
        'result': '200 OK'
      },
      {
        'name': 'Username error',
        'payload': {
          'account_email': 'fake_user_name',
          'account_password': 'uencodemo'
        },
        'result': '400 Invalid account and/or password'
      },
      {
        'name': 'Password error',
        'payload': {
          'account_email': 'uencodemo@ozzmedia.com',
          'account_password': 'fake_password'
        },
        'result': '400 Invalid account and/or password'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'NodeActivate',
    'url': 'node/activate',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'NodeDeactivate',
    'url': 'node/deactivate',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  }
]
