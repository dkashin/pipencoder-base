
Tools = [
  {
    'name': 'ToolsUpdateCheck',
    'url': 'tools/update_check',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'ToolsUpdateApply',
    'url': 'tools/update_apply',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'delay': 5,
        'result': '200'
      }
    ]
  },
  {
    'name': 'ToolsSystemStats',
    'url': 'tools/system_stats',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'ToolsDRMKeygen',
    'url': 'tools/drm_keygen',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'ToolsAppRestart',
    'url': 'tools/app_restart',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'delay': 10,
        'result': '200 OK'
      }
    ]
  },
  {
    'name': 'ToolsSystemReboot',
    'url': 'tools/system_reboot',
    'cases': [
      {
        'name': 'Regular',
        'payload': {},
        'result': '200 OK'
      }
    ]
  }
]

