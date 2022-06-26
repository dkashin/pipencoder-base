
Media = [
  {
    'name': 'MediaInfo',
    'url': 'media/info',
    'cases': [
      {
        'name': 'Clip',
        'payload': {
          'media_type': 'Clip',
          'media': '01_please_stand_by_480.ts'
        },
        'result': '200 OK'
      },
      {
        'name': 'Image',
        'payload': {
          'media_type': 'Image',
          'media': '01_please_stand_by_480.jpg'
        },
        'result': '200 OK'
      },
      {
        'name': 'URL',
        'payload': {
          'media_type': 'URL',
          'media': 'http://ott-cdn.ucom.am/s6/index.m3u8'
        },
        'delay': 5,
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': { 'key_error': 'value_error' },
        'result': '400 Required key(s)'
      },
      {
        'name': 'JSON value error',
        'payload': {
          'media_type': 'Clip',
          'media': 'value_error'
        },
        'result': '400 No such file or directory'
      }
    ]
  },
  {
    'name': 'MediaLocal',
    'url': 'media/local',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  }
]
