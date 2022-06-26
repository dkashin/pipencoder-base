
Job = [
  {
    'name': 'JobAdd',
    'url': 'job/add',
    'cases': [
      {
        'name': 'Single Profile',
        'payload': {
          'job_start': False,
          'job_data': {
            'sid': 1,
            'job_name': 'Single Profile | Multi Targets',
            'abort_on_errors': True,
            'abort_on_empty_output': True,
            'ignore_unknown': True,
            'max_error_rate': '0.75',
            'check_source': True,
            'check_target': True,
            'check_timeout': 20,
            'source_main': 'test_main.ts',
            'source_main_type': 'Clip',
            'source_main_decoder': None,
            'source_main_decoder_deinterlace': None,
            'source_main_decoder_scale': None,
            'source_main_decoder_err_detect': None,
            'source_main_loop': True,
            'source_main_udp_overrun': False,
            'source_main_udp_buffer': 4000,
            'source_main_udp_timeout': 10,
            'source_main_srt_mode': 'caller',
            'source_main_srt_passphrase': None,
            'source_main_http_reconnect': True,
            'source_main_merge_pmt_versions': True,
            'source_main_ext': None,
            'source_bak': 'test_backup.ts',
            'source_bak_type': 'URL',
            'source_bak_decoder': None,
            'source_bak_decoder_deinterlace': None,
            'source_bak_decoder_scale': None,
            'source_bak_decoder_err_detect': None,
            'source_bak_loop': True,
            'source_bak_udp_overrun': True,
            'source_bak_udp_buffer': 4000,
            'source_bak_udp_timeout': 10,
            'source_bak_srt_mode': 'caller',
            'source_bak_srt_passphrase': None,
            'source_bak_http_reconnect': True,
            'source_bak_merge_pmt_versions': True,
            'source_fail': 'test_failover.ts',
            'source_fail_type': 'Clip',
            'source_fail_decoder': None,
            'source_fail_decoder_deinterlace': None,
            'source_fail_decoder_scale': None,
            'source_fail_decoder_err_detect': None,
            'source_fail_loop': True,
            'source_fail_udp_overrun': False,
            'source_fail_udp_buffer': 4000,
            'source_fail_udp_timeout': 10,
            'source_fail_srt_mode': 'caller',
            'source_fail_srt_passphrase': None,
            'source_fail_http_reconnect': True,
            'source_fail_merge_pmt_versions': True,
            'source_active': 'main',
            'source_main_bak_rr': True,
            'thumb_interval': 50,
            'thumb_render': 'libavcodec'
          },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '480x360',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata': {
                'service_name': 'TestService',
                'service_provider': 'pipencoder'
              },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'stream_650',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                },
                {
                  'target_type': 'Stream',
                  'stream_type': 'RTMP',
                  'stream_name': 'stream_650',
                  'stream_app': 'test_app',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd'
                },
                {
                  'target_type': 'Stream',
                  'stream_type': 'UDP',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5,
                  'udp_ip': '233.10.10.10',
                  'udp_port': 5000,
                  'udp_pkt_size': 1316
                },
                {
                  'target_type': 'Stream',
                  'stream_type': 'SRT',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5,
                  'srt_ip': '192.168.10.10',
                  'srt_port': 7000,
                  'srt_maxbw': 0,
                  'srt_mode': 'caller',
                  'srt_passphrase': None,
                  'srt_pbkeylen': 0,
                  'srt_pkt_size': 1316
                }
              ]
            }
          ]
        },
        'result': '200 OK'
      },
      {
        'name': 'Multi Profile ABR',
        'payload': {
          'job_start': False,
          'job_data': {
            'sid': 2,
            'job_name': 'Multi Profile ABR',
            'abort_on_errors': True,
            'abort_on_empty_output': True,
            'ignore_unknown': True,
            'max_error_rate': '0.75',
            'check_source': True,
            'check_target': True,
            'check_timeout': 20,
            'source_main': 'test_main.ts',
            'source_main_type': 'Clip',
            'source_main_decoder': None,
            'source_main_decoder_deinterlace': None,
            'source_main_decoder_scale': None,
            'source_main_decoder_err_detect': None,
            'source_main_loop': True,
            'source_main_udp_overrun': False,
            'source_main_udp_buffer': 4000,
            'source_main_udp_timeout': 10,
            'source_main_srt_mode': 'caller',
            'source_main_srt_passphrase': None,
            'source_main_http_reconnect': True,
            'source_main_merge_pmt_versions': True,
            'source_main_ext': None,
            'source_bak': 'test_backup.ts',
            'source_bak_type': 'URL',
            'source_bak_decoder': None,
            'source_bak_decoder_deinterlace': None,
            'source_bak_decoder_scale': None,
            'source_bak_decoder_err_detect': None,
            'source_bak_loop': True,
            'source_bak_udp_overrun': True,
            'source_bak_udp_buffer': 4000,
            'source_bak_udp_timeout': 10,
            'source_bak_srt_mode': 'caller',
            'source_bak_srt_passphrase': None,
            'source_bak_http_reconnect': True,
            'source_bak_merge_pmt_versions': True,
            'source_fail': 'test_failover.ts',
            'source_fail_type': 'Clip',
            'source_fail_decoder': None,
            'source_fail_decoder_deinterlace': None,
            'source_fail_decoder_scale': None,
            'source_fail_decoder_err_detect': None,
            'source_fail_loop': True,
            'source_fail_udp_overrun': False,
            'source_fail_udp_buffer': 4000,
            'source_fail_udp_timeout': 10,
            'source_fail_srt_mode': 'caller',
            'source_fail_srt_passphrase': None,
            'source_fail_http_reconnect': True,
            'source_fail_merge_pmt_versions': True,
            'source_active': 'main',
            'source_main_bak_rr': True,
            'hls_abr_active': True,
            'hls_abr_basename': 'test_abr',
            'hls_abr_list_name': 'master',
            'hls_abr_server': '02cf0de949f44579847472fd437f5ebd',
            'thumb_interval': 50,
            'thumb_render': 'libavcodec'
          },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '480x360',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'stream_650',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '480x360',
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            },
            {
              'vpreset': 'H264_1300',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '1280x720',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'stream_1300',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '1280x720',
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            }
          ]
        },
        'result': '200 OK'
      },
      {
        'name': 'Multi Profile ABR DRM',
        'payload': {
          'job_start': False,
          'job_data': {
            'sid': 3,
            'job_name': 'Multi Profile ABR DRM',
            'abort_on_errors': True,
            'abort_on_empty_output': True,
            'ignore_unknown': True,
            'max_error_rate': '0.75',
            'check_source': True,
            'check_target': True,
            'check_timeout': 20,
            'source_main': 'test_main.ts',
            'source_main_type': 'Clip',
            'source_main_decoder': None,
            'source_main_decoder_deinterlace': None,
            'source_main_decoder_scale': None,
            'source_main_decoder_err_detect': None,
            'source_main_loop': True,
            'source_main_udp_overrun': False,
            'source_main_udp_buffer': 4000,
            'source_main_udp_timeout': 10,
            'source_main_srt_mode': 'caller',
            'source_main_srt_passphrase': None,
            'source_main_http_reconnect': True,
            'source_main_merge_pmt_versions': True,
            'source_main_ext': None,
            'source_bak': 'test_backup.ts',
            'source_bak_type': 'URL',
            'source_bak_decoder': None,
            'source_bak_decoder_deinterlace': None,
            'source_bak_decoder_scale': None,
            'source_bak_decoder_err_detect': None,
            'source_bak_loop': True,
            'source_bak_udp_overrun': True,
            'source_bak_udp_buffer': 4000,
            'source_bak_udp_timeout': 10,
            'source_bak_srt_mode': 'caller',
            'source_bak_srt_passphrase': None,
            'source_bak_http_reconnect': True,
            'source_bak_merge_pmt_versions': True,
            'source_fail': 'test_failover.ts',
            'source_fail_type': 'Clip',
            'source_fail_decoder': None,
            'source_fail_decoder_deinterlace': None,
            'source_fail_decoder_scale': None,
            'source_fail_decoder_err_detect': None,
            'source_fail_loop': True,
            'source_fail_udp_overrun': False,
            'source_fail_udp_buffer': 4000,
            'source_fail_udp_timeout': 10,
            'source_fail_srt_mode': 'caller',
            'source_fail_srt_passphrase': None,
            'source_fail_http_reconnect': True,
            'source_fail_merge_pmt_versions': True,
            'source_active': 'main',
            'source_main_bak_rr': True,
            'hls_abr_active': True,
            'hls_abr_basename': 'test_abr_drm',
            'hls_abr_list_name': 'master',
            'hls_abr_server': '02cf0de949f44579847472fd437f5ebd',
            'hls_drm_active': True,
            'hls_drm_type': 'AES-128',
            'hls_drm_key_type': 'Local',
            'hls_drm_key': 'f0098f47ecd9315233f81dc09d0b8dd0',
            'hls_drm_key_iv': '5d5395a0eebfd4c1a1bcb64f51cb6d97',
            'hls_drm_key_user': None,
            'hls_drm_key_password': None,
            'thumb_interval': 50,
            'thumb_render': 'libavcodec'
          },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '480x360',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'stream_650',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '480x360',
                  'hls_drm_asset': True,
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            },
            {
              'vpreset': 'H264_1300',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '1280x720',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'stream_1300',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '1280x720',
                  'hls_drm_asset': True,
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            }
          ]
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': { 'key_error': 'value_error' },
        'result': '400 Required key(s)'
      },
      {
        'name': 'Job data error',
        'payload': {
          'job_start': False,
          'job_data': { 'key_error': 'value_error' },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'stream_type': 'HLS',
                  'stream_name': 'test_stream',
                  'hls_list_name': 'play'
                }
              ]
            }
          ]
        },
        'result': '400 Incorrect job data'
      },
      {
        'name': 'Profile data error',
        'payload': {
          'job_start': False,
          'job_data': { 'job_name': 'Single Profile' },
          'profile': [ { 'key_error': 'value_error' } ]
        },
        'result': '400 Profile #0'
      },
      {
        'name': 'Target data error',
        'payload': {
          'job_start': False,
          'job_data': { 'job_name': 'Single Profile' },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'target': [ { 'key_error': 'value_error' } ]
            }
          ]
        },
        'result': '400 Target #0'
      }
    ]
  },
  {
    'name': 'JobList',
    'url': 'job/list',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'filter': [
            { 'field': 'id', 'value': None, 'type': 'or' },
            { 'field': 'sid', 'value': None, 'type': 'or' },
            { 'field': 'job_name', 'value': None, 'type': 'or' },
            { 'field': 'source_global', 'value': None, 'type': 'or' },
            { 'field': 'target_global', 'value': None, 'type': 'or' },
            { 'field': 'video_pid_global', 'value': None, 'type': 'or' },
            { 'field': 'audio_pid_global', 'value': None, 'type': 'or' },
            { 'field': 'dpid_global', 'value': None, 'type': 'or' },
            { 'field': 'vpreset', 'value': None, 'type': 'or' },
            { 'field': 'apreset', 'value': None, 'type': 'or' },
            { 'field': 'venc_di', 'value': None, 'type': 'or' },
            { 'field': 'venc_psize', 'value': None, 'type': 'or' },
            { 'field': 'nvenc_gpu', 'value': None, 'type': 'or' },
            { 'field': 'stream_srv', 'value': None, 'type': 'or' },
            { 'field': 'stream_type', 'value': None, 'type': 'or' },
            { 'field': 'hls_abr_active', 'value': None, 'type': 'or' },
            { 'field': 'hls_drm_active', 'value': None, 'type': 'or' },
            { 'field': 'run_status', 'value': None, 'type': 'or' },
            { 'field': 'retries', 'value': None, 'type': 'or' }
          ],
          'sort_by': 'sid',
          'sort_by_order': 'asc',
          'per_page': 10,
          'act_page': 1,
          'hash': None
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON value error',
        'payload': {
          'filter': [{
            'field': 'value_error',
            'value': None,
            'type': 'or'
          }],
          'sort_by': 'value_error'
        },
        'result': '400 Exception error'
      }
    ]
  },
  {
    'name': 'JobStatus',
    'url': 'job/status',
    'cases': [
      {
        'name': 'Single job',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Multi jobs',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Job ID error',
        'payload': { 'id': [ 'value_error' ] },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'JobStart',
    'url': 'job/start',
    'cases': [
      {
        'name': 'Single job',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Multi jobs',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Job ID error',
        'payload': { 'id': [ 'value_error' ] },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'JobRestart',
    'url': 'job/restart',
    'cases': [
      {
        'name': 'Single job',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Multi jobs',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Job ID error',
        'payload': { 'id': [ 'value_error' ] },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'JobStop',
    'url': 'job/stop',
    'cases': [
      {
        'name': 'Single job',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Multi jobs',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Job ID error',
        'payload': { 'id': [ 'value_error' ] },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  },
  {
    'name': 'JobUpdate',
    'url': 'job/update',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'restart_required': True,
          'job_data': {
            'id': None,
            'sid': 4,
            'job_name': 'Multi Profile ABR DRM Edited',
            'abort_on_errors': True,
            'abort_on_empty_output': True,
            'ignore_unknown': True,
            'max_error_rate': '0.75',
            'check_source': True,
            'check_target': True,
            'check_timeout': 20,
            'source_main': 'test_main.ts',
            'source_main_type': 'Clip',
            'source_main_decoder': None,
            'source_main_decoder_deinterlace': None,
            'source_main_decoder_scale': None,
            'source_main_decoder_err_detect': None,
            'source_main_loop': True,
            'source_main_udp_overrun': False,
            'source_main_udp_buffer': 4000,
            'source_main_udp_timeout': 10,
            'source_main_srt_mode': 'caller',
            'source_main_srt_passphrase': None,
            'source_main_http_reconnect': True,
            'source_main_merge_pmt_versions': True,
            'source_main_ext': None,
            'source_bak': 'test_backup.ts',
            'source_bak_type': 'URL',
            'source_bak_decoder': None,
            'source_bak_decoder_deinterlace': None,
            'source_bak_decoder_scale': None,
            'source_bak_decoder_err_detect': None,
            'source_bak_loop': True,
            'source_bak_udp_overrun': True,
            'source_bak_udp_buffer': 4000,
            'source_bak_udp_timeout': 10,
            'source_bak_srt_mode': 'caller',
            'source_bak_srt_passphrase': None,
            'source_bak_http_reconnect': True,
            'source_bak_merge_pmt_versions': True,
            'source_fail': 'test_failover.ts',
            'source_fail_type': 'Clip',
            'source_fail_decoder': None,
            'source_fail_decoder_deinterlace': None,
            'source_fail_decoder_scale': None,
            'source_fail_decoder_err_detect': None,
            'source_fail_loop': True,
            'source_fail_udp_overrun': False,
            'source_fail_udp_buffer': 4000,
            'source_fail_udp_timeout': 10,
            'source_fail_srt_mode': 'caller',
            'source_fail_srt_passphrase': None,
            'source_fail_http_reconnect': True,
            'source_fail_merge_pmt_versions': True,
            'source_active': 'main',
            'source_main_bak_rr': True,
            'hls_abr_active': True,
            'hls_abr_basename': 'test_abr_drm',
            'hls_abr_list_name': 'master',
            'hls_abr_server': '02cf0de949f44579847472fd437f5ebd',
            'hls_drm_active': True,
            'hls_drm_type': 'AES-128',
            'hls_drm_key_type': 'Local',
            'hls_drm_key': 'f0098f47ecd9315233f81dc09d0b8dd0',
            'hls_drm_key_iv': '5d5395a0eebfd4c1a1bcb64f51cb6d97',
            'hls_drm_key_user': None,
            'hls_drm_key_password': None,
            'thumb_interval': 25,
            'thumb_render': 'libavcodec'
          },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '480x360',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'edited_stream_650',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '480x360',
                  'hls_drm_asset': True,
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            },
            {
              'vpreset': 'H264_1300',
              'apreset': 'AAC_LC_64',
              'dpreset': 'copy',
              'main_vpid': '#256',
              'main_apid': None,
              'main_dpid': None,
              'bak_vpid': '#256',
              'bak_apid': None,
              'bak_dpid': None,
              'fail_vpid': '#256',
              'fail_apid': None,
              'fail_dpid': None,
              'venc_psize': '1280x720',
              'venc_di': 'send_frame',
              'nvenc_gpu': None,
              'stream_metadata':
                {
                  'service_name': 'TestService',
                  'service_provider': 'pipencoder'
                },
              'stream_pids': None,
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_type': 'HLS',
                  'stream_name': 'edited_stream_1300',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'hls_abr_asset': True,
                  'hls_abr_bandwidth': 665600,
                  'hls_abr_codecs': 'avc1.4d401f',
                  'hls_abr_resolution': '1280x720',
                  'hls_drm_asset': True,
                  'hls_list_name': 'play',
                  'hls_list_size': 8,
                  'hls_seg_abs_path': False,
                  'hls_seg_format': 'Timestamp',
                  'hls_seg_name': '%Y%m%d%H%M%S',
                  'hls_seg_time': 8,
                  'mpegts_flags': None,
                  'mpegts_muxrate': None,
                  'mpegts_pat_period': 0.1,
                  'mpegts_pcr_period': 20,
                  'mpegts_sdt_period': 0.5
                }
              ]
            }
          ]
        },
        'result': '200 OK'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      },
      {
        'name': 'Job ID error',
        'payload': {
          'restart_required': False,
          'job_data': { 'id': 'value_error' },
          'profile': [{}]
        },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'Job data error',
        'payload': {
          'restart_required': False,
          'job_data': { 'key_error': 'value_error' },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'target': [
                {
                  'target_type': 'Stream',
                  'stream_srv': '02cf0de949f44579847472fd437f5ebd',
                  'stream_type': 'HLS',
                  'stream_name': 'test_stream',
                  'hls_list_name': 'play'
                }
              ]
            }
          ]
        },
        'result': '400 Incorrect job data'
      },
      {
        'name': 'Profile data error',
        'payload': {
          'restart_required': False,
          'job_data': { 'id': None },
          'profile': [ { 'key_error': 'value_error' } ]
        },
        'result': '400 Profile #0'
      },
      {
        'name': 'Target data error',
        'payload': {
          'restart_required': False,
          'job_data': {
            'id': None,
            'job_name': 'Single Profile'
          },
          'profile': [
            {
              'vpreset': 'H264_650',
              'apreset': 'AAC_LC_64',
              'target': [ { 'key_error': 'value_error' } ]
            }
          ]
        },
        'result': '400 Target #0'
      }
    ]
  },
  {
    'name': 'ToolsGetLog',
    'url': 'tools/get_log',
    'cases': [
      {
        'name': 'Regular',
        'payload': {
          'log_dir': 'jobs',
          'log_name': None,
          'read_from': 'end',
          'show_lines': 10,
          'offset': 0
        },
        'result': '200 OK'
      },
      {
        'name': 'Log name error',
        'payload': {
          'log_dir': 'jobs',
          'log_name': 'value_error',
          'read_from': 'end',
          'show_lines': 10,
          'offset': 0
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
          'log_dir': 'jobs',
          'log_name': None,
          'read_from': 'end',
          'show_lines': 'value_error',
          'offset': 'value_error'
        },
        'result': 'HTTP 400 Exception'
      }
    ]
  },
  {
    'name': 'JobDelete',
    'url': 'job/delete',
    'cases': [
      {
        'name': 'Single job',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Multi jobs',
        'payload': { 'id': None },
        'result': '200 OK'
      },
      {
        'name': 'Job ID error',
        'payload': { 'id': [ 'value_error' ] },
        'result': '400 No job(s) to process'
      },
      {
        'name': 'JSON key error',
        'payload': {},
        'result': '400 Required key(s)'
      }
    ]
  }
]

