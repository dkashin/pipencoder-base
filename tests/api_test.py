
import sys, os, logging, time, requests, json

from requests.exceptions import RequestException
from logging import Formatter, NullHandler
from logging.handlers import RotatingFileHandler

sys.path.append('tests')

from test_auth import Login, Logout
from test_job import Job
from test_media import Media
from test_node import Node
from test_preset import AVPreset
from test_server import Server
from test_settings import Settings
from test_tools import Tools
from test_user import User


class Color:
   PURPLE = '\033[1;35;48m'
   CYAN = '\033[1;36;48m'
   BOLD = '\033[1;37;48m'
   BLUE = '\033[1;34;48m'
   GREEN = '\033[1;32;48m'
   YELLOW = '\033[1;33;48m'
   RED = '\033[1;31;48m'
   BLACK = '\033[1;30;48m'
   UNDERLINE = '\033[4;37;48m'
   END = '\033[1;37;0m'


### Log manager class  ###
class LogManager(object):


  def LogNull(self):
    logger = logging.getLogger()
    logger.setLevel(10)
    logger.addHandler(NullHandler())
    logger.debug('[LOG] Logger: Null handler created')
    return logger


  def LogClose(self, logger = None, area = None):
    try:
      if area:
        logger = logging.getLogger(area)
      if logger.handlers:
        logger.debug('[LOG] Logger: Handlers removing (' + str(area) + ')')
        for handler in logger.handlers:
          logger.removeHandler(handler)
    except:
      pass
      #raise


  def LogOpen(self, area = None, log_level = 10, log_file = None):
    try:
      logger = logging.getLogger(area)
      self.LogClose(logger = logger, area = area)
      if not logger.handlers:
        logger.setLevel(log_level)
        formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        handler = RotatingFileHandler(log_file, mode = 'a', maxBytes = 1048576, backupCount = 1)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        #logger.debug('[LOG] Logger: Handler created (' + str(area) + ')')
    except:
      logger = self.LogNull()
      #raise
    return logger


### JSON tools ###
class JSONTools(object):


  def __init__(self, logger):
    if logger:
      self.logger = logger
    else:
      self.logger = _LogManager.LogNull()


  # Check request with JSON
  def CheckRequest(self, request = None):
    try:
      json_data = request.get_json() or {}
      msg = 'OK'
    except:
      json_data = {}
      msg = 'Request has no JSON data'
      raise
    return json_data, msg


  # Check JSON keys
  def CheckKeys(self, json_data = {}, match_keys = []):
    result = False
    try:
      if match_keys:
        json_keys = list(json_data.keys())
        missing_json_keys = [ key for key in match_keys if not key in json_keys ]
        if missing_json_keys:
          return False, 'Required key(s): ' + str(missing_json_keys)
      msg = 'OK'
      result = True
    except:
      msg = 'JSON format error (CheckKeys)'
      raise
    return result, msg


  # Check JSON data
  def CheckIntegrity(self, request = None, json_data = {}, match_keys = []):
    result = False
    if request:
      json_data, msg = self.CheckRequest(request = request)
    if not json_data == None:
      result, msg = self.CheckKeys(json_data = json_data, match_keys = match_keys)
    else:
      msg = 'JSON format error (CheckIntegrity)'
    return result, msg


_LogManager = LogManager()
test_logger = _LogManager.LogOpen(area = 'test', log_file = 'test_report.log')
_JSONTools = JSONTools(logger = test_logger)


# System test class
class TestAPI(object):

  def __init__(self, logger, api_path):
    if logger:
      self.logger = logger
    else:
      self.logger = _LogManager.LogNull()
    self.api_path = api_path
    self.api_key = None
    self.job_id = []
    self.user_id = None
    self.server_id = None
    self.settings_id = None


  def Run(self, url = '', headers = { 'Content-Type': 'application/json', 'User-Agent': 'Mozilla' }, payload = {}):
    response = {}
    try:
      self.logger.info('   Payload: ' + str(payload))
      r = requests.post(url, headers = headers, json = payload, timeout = 5)
      http_code = f'HTTP {r.status_code} {r.reason}'
#      self.logger.info('  Response: HTTP ' + str(r.status_code))
      if r.status_code >= 200 and r.status_code < 300:
        try:
          response = r.json()
          self.logger.info(f'   Response: {response}')
          json_check, status = _JSONTools.CheckIntegrity(json_data = response)
          if json_check:
            status = http_code
        except:
          status = f'{http_code} JSON format error (r.json())'
        self.logger.info(f'   Result: {status}')
      else:
        status = http_code
        self.logger.error(f'  Result: {http_code}')
    except RequestException as e:
      status = f'Failed (RequestException)'
      self.logger.error(f'  Result: Failed ({e})')
    except:
      status = f'Failed (exception)'
      self.logger.error(f'  Result: Failed (exception)')
      raise
    return status, response


  def CaseRequest(self, test = None, case = None):
    case_payload = case.get('payload')
    case_name = case.get('name')
    if self.api_key:
      case_payload['api_key'] = self.api_key
    if test in [ 'ServerUpdate', 'ServerDelete' ]:
      if case_name != 'JSON key error':
        if case_payload.get('id') == None and self.server_id:
          case_payload['id'] = self.server_id
    if test in [ 'JobStatus', 'JobStart', 'JobRestart', 'JobStop', 'JobDelete' ]:
      if case_payload.get('id') == None and self.job_id:
        if case_name != 'JSON key error':
          if case_name == 'Multi jobs':
            if test == 'JobDelete':
              case_payload['id'] = [ self.job_id[1], self.job_id[2] ]
            else:
              case_payload['id'] = self.job_id
          else:
            case_payload['id'] = [ self.job_id[0] ]
    if test == 'JobUpdate':
      if case_payload.get('job_data'):
        if case_payload['job_data'].get('id') == None and self.job_id:
          case_payload['job_data']['id'] = self.job_id[2]
    if test == 'ToolsGetLog':
      if case_payload.get('log_name') == None and self.job_id:
        case_payload['log_name'] = f'{self.job_id[0]}_job.log'
    if test == 'SettingsSave':
      if case_payload.get('id') == None and self.settings_id:
        case_payload['id'] = self.settings_id
    if test in [ 'UserUpdate', 'UserDelete' ]:
      if case_name != 'JSON key error':
        if case_payload.get('id') == None and self.user_id:
          case_payload['id'] = self.user_id


  def CaseResponse(self, test = None, case = None, response = {}):
    case_name = case['name']
    if test == 'AuthLogin' and case_name == 'Regular':
      if 'api_key_data' in list(response.keys()):
        if 'api_key' in list(response['api_key_data'].keys()):
          self.api_key = response['api_key_data']['api_key']
    if test == 'ServerAdd' and case_name == 'Regular':
      if 'server_id' in list(response.keys()):
        self.server_id = response.get('server_id')
    if (test == 'JobAdd') and (case_name in [ 'Single Profile', 'Multi Profile ABR', 'Multi Profile ABR DRM']):
      if 'job_id' in list(response.keys()):
        self.job_id.append(response.get('job_id'))
    if test == 'SettingsLoad' and case_name == 'Regular':
      if 'settings' in list(response.keys()):
        if 'id' in list(response['settings'].keys()):
          self.settings_id = response['settings'].get('id')
    if test == 'UserAdd' and case_name == 'Regular':
      if 'user_id' in list(response.keys()):
        self.user_id = response.get('user_id')


  def RunAll(self, tests = [], skip = [], selected = []):
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla'
    }
    header_info = str(len(tests)) + ' test(s) available'
    if selected:
      header_info += ' / ' + str(len(selected)) + ' selected'
    if skip:
      header_info += ' / ' + str(len(skip)) + ' skipped'
    print(header_info)
    self.logger.info('----------------------------------')
    self.logger.info(header_info)
    self.logger.info('----------------------------------')
    self.logger.info('')
    test_count = 0
    cases_count = 0
    for test in tests:
      if not selected or test['name'] in selected:
        url = os.path.join(self.api_path, test['url'])
        if test['name'] in skip:
          print(('API: ' + test['name'] + ' [ SKIPPED ]'))
          self.logger.info('-------- Test start: ' + test['name'] + ' --------')
          self.logger.info('[ SKIPPED ]')
          self.logger.info('-------- Test end: ' + test['name'] + ' --------')
        else:
          self.logger.info('-------- Test start: ' + test['name'] + ' --------')
          self.logger.info('URL: ' + url)
          self.logger.info('Headers: ' + str(headers))
          print(('API: ' + test['name']))
          for case in test['cases']:
            self.logger.info('Case: ' + case['name'])
            self.CaseRequest(test = test['name'], case = case)
            if 'delay' in list(case.keys()):
              case_delay = case['delay']
              self.logger.info('   Delay: ' + str(case_delay) + ' seconds')
              time.sleep(case['delay'])
            result, response = self.Run(url = url, headers = headers, payload = case['payload'])
            if response:
              self.CaseResponse(test = test['name'], case = case, response = response)
            cases_count += 1
            case_name = case.get('name')
            if case.get('result') in result:
              status = f'{Color.GREEN}Pass{Color.END}'
              self.logger.info(f'   Status: Pass')
            else:
              status = f'{Color.RED}Fail{Color.END}'
              self.logger.info(f'   Status: Fail')
            print(f'{f"  Case: {case_name}":<30}{f"Status: {status}":<10} ({result})')
          self.logger.info('-------- Test end: ' + test['name'] + ' --------')
          self.logger.info('')
          test_count += 1
    footer_info = str(test_count) + ' test(s) / ' + str(cases_count) + ' case(s) completed'
    print(footer_info)
    self.logger.info('----------------------------------')
    self.logger.info(footer_info)
    self.logger.info('----------------------------------')

# Auth:
#selected = [ 'AuthLogin', 'AuthLoggedUser', 'AuthLogout' ]

# Job:
#selected = [ 'AuthLogin', 'JobAdd', 'JobList', 'JobStatus', 'JobStart', 'JobRestart', 'JobStop', 'JobUpdate', 'ToolsGetLog', 'JobDelete' ]

# Media:
#selected = [ 'AuthLogin', 'MediaInfo', 'MediaLocal' ]

# Node:
#selected = [ 'AuthLogin', 'NodeAuth', 'NodeActivate', 'NodeDeactivate' ]

# AV Presets:
#selected = [ 'AuthLogin', 'AVPresetList', 'AVPresetData', 'AVPresetAdd', 'AVPresetUpdate', 'AVPresetDelete' ]

# Server:
#selected = [ 'AuthLogin', 'ServerAdd', 'ServerList', 'ServerUpdate', 'ServerDelete' ]

# Settings:
#selected = [ 'AuthLogin', 'SettingsLoad', 'SettingsSave' ]

# Tools:
#selected = [ 'AuthLogin', 'ToolsUpdateCheck', 'ToolsUpdateApply', 'ToolsSystemStats', 'ToolsDRMKeygen', 'ToolsAppRestart', 'ToolsSystemReboot' ]

# User:
#selected = [ 'AuthLogin', 'UserAdd', 'UserList', 'UserUpdate', 'UserDelete' ]

selected = []

# Skip tests
skip = [ 'ToolsSystemReboot' ]

#API path and veersions
api_path = 'http://localhost:8077/api/v1'

# All available tests in order
tests = Login + Job + Media + Node + AVPreset + Server + Settings + User + Tools + Logout

TestAPI = TestAPI(logger = test_logger, api_path = api_path).RunAll(tests = tests, selected = selected, skip = skip)

