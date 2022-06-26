
Server = [
  {
    'name': 'ServerAdd',
    'url': 'server/add',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'name': 'TestServer',
          'ip': 'test.ip',
          'hls_srv': 'http://test.ip/hls',
          'rtmp_srv': 'rtmp://test.ip:1935/app/stream'
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'ServerList',
    'url': 'server/list',
    'cases': [
      {
        'name': 'Regular',
        'payload': { 'hash': None },
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'ServerUpdate',
    'url': 'server/update',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'id': None,
          'ip': 'test.ip',
          'name': 'TestServer',
          'jobs_restart': True,
          'hls_srv': 'http://test.ip/hls',
          'rtmp_srv': 'rtmp://test.ip:1935/app/stream'
        },
        'result': '200 OK'
      },
      {
        'name': 'ID error',
        'payload': {
          'id': 'value_error',
          'ip': 'test.ip',
          'name': 'TestServer',
          'jobs_restart': False
        },
        'result': '400 Server ID is not found'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'ServerDelete',
    'url': 'server/delete',
    'cases': [
      {
        'name': 'Regular',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'ID value error',
        'payload': { 'id': 'value_error' },
        'result': '400 Server ID is not found'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  }
]

