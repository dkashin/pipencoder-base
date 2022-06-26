
AVPreset = [
  {
    'name': 'AVPresetList',
    'url': 'preset/list',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'AVPresetData',
    'url': 'preset/data',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'AVPresetAdd',
    'url': 'preset/add',
    'cases': [
      {
        'name': 'Test video preset',
        'payload': {
          'preset_type': 'video',
          'preset_data': {
            'type': 'video',
            'name': 'test_video_preset',
            'description': 'test video preset',
            'vcodec': 'h264_nvenc',
            'vpreset': 'llhq',
            'vbitrate': 4000,
            'maxrate': 8000,
            'vbuffer': 8000,
            'vprofile': 'high',
            'level': '4.1',
            'cbr': '1',
            'keyframes': 2,
            'gop': 120,
            'subsample': 'yuv420p',
            'cc_copy': True,
            'vcustom': 'custom video encoder options'
          }
        },
        'result': '200 OK'
      },
      {
        'name': 'Test audio preset',
        'payload': {
          'preset_type': 'audio',
          'preset_data': {
            'type': 'audio',
            'name': 'test_audio_preset',
            'acodec': 'libfdk_aac',
            'abitrate': 64,
            'channels': 2,
            'sample_rate': 48000,
            'acustom': 'custom audio encoder options',
            'description': 'test audio preset'
          }
        },
        'result': '200 OK'
      },
      {
        'name': 'Preset name error',
        'payload': {
            'preset_type': 'video',
            'preset_data': { 'name': 'test_video_preset' }
        },
        'result': '400 Preset name already exists'
      },
      {
        'name': 'Path error',
        'payload': {
          'preset_type': 'value_error',
          'preset_data': { 'name': 'test_video_preset' }
        },
        'result': '400 Preset is not found'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'AVPresetUpdate',
    'url': 'preset/update',
    'cases': [
      {
        'name': 'Test video preset',
        'payload': {
          'preset_type': 'video',
          'preset_data': {
            'type': 'video',
            'name': 'test_video_preset',
            'description': 'test video preset',
            'vcodec': 'h264_nvenc',
            'vpreset': 'llhq',
            'vbitrate': 4000,
            'maxrate': 8000,
            'vbuffer': 8000,
            'vprofile': 'high',
            'level': '4.1',
            'cbr': '1',
            'keyframes': 2,
            'gop': 120,
            'subsample': 'yuv420p',
            'cc_copy': True,
            'vcustom': 'custom video encoder options'
          }
        },
        'result': '200 OK'
      },
      {
        'name': 'Test audio preset',
        'payload': {
          'preset_type': 'audio',
          'preset_data': {
            'type': 'audio',
            'name': 'test_audio_preset',
            'acodec': 'libfdk_aac',
            'abitrate': 64,
            'channels': 2,
            'sample_rate': 48000,
            'acustom': 'custom audio encoder options',
            'description': 'test audio preset'
          }
        },
        'result': '200 OK'
      },
      {
        'name': 'Path error',
        'payload': {
          'preset_type': 'value_error',
          'preset_data': { 'name': 'test_video_preset' }
        },
        'result': '400 Preset is not found'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'AVPresetDelete',
    'url': 'preset/delete',
    'cases': [
      {
        'name': 'Test video preset',
        'payload': {
          'preset_name': 'test_video_preset',
          'preset_type': 'video'
        },
        'result': '200 OK'
      },
      {
        'name': 'Test audio preset',
        'payload': {
          'preset_name': 'test_audio_preset',
          'preset_type': 'audio'
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      },
      {
        'name': 'JSON value error',
        'payload': {
          'preset_name': 'value_error',
          'preset_type': 'value_error'
        },
        'result': '400 Preset is not found'
      }
    ]
  }
]
