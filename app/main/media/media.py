
import os, shlex
from subprocess import STDOUT, check_output, CalledProcessError

from main.tools import _JSONTools, _FileTools
from main.check import _CheckTools
from main.common.config import app_config
from main.common.log import LogManager


class MediaManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Device(s) info
  def DeviceInfo(self, dev_brand = None, dev_name = None):
    result = False
    dev_info = []
    dev_features = []
    try:
      cmd = [ app_config.FFMPEG_BIN, '-hide_banner', '-f', dev_brand, '-list_formats', '1', '-i', dev_name ]
      dev_info = check_output(cmd, close_fds = True, stderr = STDOUT).splitlines().decode()
    except CalledProcessError as e:
      dev_info = str(e.output).decode().splitlines()
    except:
      self.logger.error('[MediaManager] DeviceInfo exception error')
      dev_status = 'Device query error (' + dev_brand + ')'
      raise
      return dev_features, dev_status
    for dev_line in dev_info:
      if 'fps' in dev_line:
        dev_features.append(dev_line)
    if dev_features:
      dev_status = 'OK'
    else:
      dev_info.pop(0)
      self.logger.debug('[MediaManager] DeviceInfo: dev_info (' + str(dev_info) + ')')
      dev_status = ''.join([ err.replace(err[ err.find('[') : err.find(']') + 2 ], '') for err in dev_info ])
    self.logger.error('[MediaManager] DeviceInfo: dev_status (' + str(dev_status) + ')')
    return dev_features, dev_status


  # Device(s) list
  def DeviceList(self):
    result = False
    devices = []
    try:
      for dev_brand in app_config.DEVICE_BRAND:
        cmd = [ app_config.FFMPEG_BIN, '-hide_banner', '-sources', dev_brand ]
        dev_list = check_output(cmd, close_fds = True, stderr = STDOUT).decode()
        if dev_list:
          dev_features = []
          dev_name = dev_brand
          dev_err_fatal = '[' + dev_brand + ' @'
          if dev_err_fatal in dev_list:
            dev_errors = dev_list.splitlines()
            dev_status = ''.join([ err.replace(err[ err.find('[') : err.find(']') + 2 ], '') for err in dev_errors if dev_err_fatal in err ])
            self.logger.debug('[MediaManager] DeviceList: Errors detected (' + str(dev_status) + ')')
          else:
            dev_list = dev_list.splitlines()
            dev_list.pop(0)
            for dev in dev_list:
              dev_name = dev[ dev.find('[') + 1 : dev.find(']') ]
              dev_features, dev_status = self.DeviceInfo(dev_brand = dev_brand, dev_name = dev_name)
          devices.append({
            'brand': dev_brand,
            'name': dev_name,
            'format_code': dev_features,
            'status': dev_status
          })
          self.logger.debug('[MediaManager] DeviceList: devices ' + str(devices))
    except CalledProcessError as e:
      self.logger.error('[MediaManager] DeviceList: CalledProcessError error (' + str(e) + ')')
    except:
      self.logger.error('[MediaManager] DeviceList exception error')
      raise
    return devices


  # Get local media list
  def MediaLocal(self, request = None, json_data = None):
    response = {}
    try:
      media_list = {
        'devices': self.DeviceList(),
        'assets': {
          'images': _FileTools.ListDir(dir = app_config.IMAGES_DIR),
          'clips': _FileTools.ListDir(dir = app_config.CLIPS_DIR)
        }
      }
      response.update(media_list)
      self.logger.debug('[MediaManager] MediaLocal: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[MediaManager] MediaLocal: ' + msg)
    return response, 400, msg


  ### Stream info ###
  def MediaInfo(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'media', 'media_type' ])
      self.logger.info('[MediaManager] MediaInfo: '  + str(json_data))
      if json_check:
        media = json_data.get('media')
        if media:
          media_type = json_data.get('media_type')
          if media_type == 'Image':
            media = os.path.join(app_config.IMAGES_DIR, media)
          elif media_type == 'Clip':
            media = os.path.join(app_config.CLIPS_DIR, media)
          self.logger.info('[MediaManager] MediaInfo: Analyzing ' + str(media))
          media_data, msg = _CheckTools.CheckFFProbe(media = media)
          if media_data:
            response.update(media_data)
            return response, 200, 'OK'
        else:
          msg = 'No media to analyze'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[MediaManager] MediaInfo: ' + msg)
    return response, 400, msg

