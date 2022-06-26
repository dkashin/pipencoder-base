
Settings = [
  {
    'name': 'SettingsLoad',
    'url': 'settings/load',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'SettingsSave',
    'url': 'settings/save',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'id': None,
          'update_path': 'http://18.188.182.187:8099/update',
          'callback_url': '',
          'default_fail_src': 'new_value',
          'default_fail_type': 'Clip',
          'default_fail_vpid': '#123',
          'default_fail_apid': '#456',
          'default_fail_dpid': '#777',
          'default_fail_decoder': 'libavcodec',
          'default_fail_decoder_err_detect': 'crccheck',
          'default_fail_loop': True,
          'default_fail_udp_overrun': True,
          'default_fail_udp_buffer': 1000,
          'default_fail_udp_timeout': 5,
          'default_srt_mode': 'Caller',
          'default_srt_passphrase': 'passphrase',
          'default_fail_merge_pmt_versions': True,
          'default_fail_http_reconnect': True,
          'smtp_host': 'localhost',
          'smtp_port': 25,
          'smtp_user': 'report@ozzmedia.tv',
          'smtp_pass': '',
          'smtp_ssl': False,
          'smtp_tls': False,
          'alarm_action': True,
          'alarm_action_email': 'dm.kashin@yandex.ru',
          'alarm_action_subject': 'Action Report',
          'alarm_action_count': 1,
          'alarm_error': True,
          'alarm_error_email': 'dm.kashin@yandex.ru',
          'alarm_error_subject': 'Error Report',
          'alarm_error_value': 1,
          'alarm_error_period': 60,
          'alarm_master': True,
          'alarm_master_email': 'dm.kashin@yandex.ru',
          'alarm_master_subject': 'Report'
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      },
      {
        'name': 'ID value error',
        'payload': {
          'id': 'value_error',
          'default_fail_src': False,
          'default_fail_type': 100
        },
        'result': '400 Settings query error'
      },
      {
        'name': 'JSON value error',
        'payload': {
          'id': None,
          'default_fail_src': False,
          'default_fail_type': 100,
          'key_error': 'value_error'
        },
        'result': '400 Exception error'
      }
    ]
  }
]

