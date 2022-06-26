
import json, requests
from requests.exceptions import RequestException

from main.tools import _ToolSet
from main.common.config import app_config
from main.common.models import Settings
from main.common.database import db_session
from main.common.log import LogManager


### Node ###
class NodeManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # API call
  def APICall(self, api = None, post_data = None):
    try:
      r = requests.post(api, headers = app_config.HEADERS_JSON, json = post_data, timeout = 3)
      try:
        response = r.json()
      except:
        response = r.text
      return response, r.status_code, r.reason
    except RequestException as e:
      msg = 'API RequestException error'
      self.logger.error('[NodeManager] APICall: RequestException error (' + str(e) + ')')
    except:
      msg = 'API exception error'
      self.logger.error('[NodeManager] APICall: API exception error')
      raise
    return {}, 400, msg


  def Auth(self, request = None, node_api_key = None):
    json_check, msg, json_data = _ToolSet.CheckIntegrity(request = request, match_keys = [ 'account_email', 'account_password' ])
    if json_check:
      self.logger.debug('[NodeManager] Auth: request ' + str(json_data))
      account_email = json_data.get('account_email')
      account_password = json_data.get('account_password')
      if account_email and account_password:
        post_data = {
          'email': account_email,
          'password': account_password,
          'api_key_options': {
            'action': 'create',
            'node_key': node_api_key or True
          }
        }
        response, code, msg = self.APICall(api = app_config.NODE_AUTH, post_data = post_data)
        self.logger.debug('[NodeManager] Auth: response ' + str(response))
        if code == 200:
          Settings.query.update({ 'node_api_key': response.get('api_key') })
          db_session.commit()
          response.pop('api_key', None)
          response.pop('expire', None)
        return response, code, msg
      else:
        msg = 'Cloud auth data is not found'
    self.logger.error('[NodeManager] Auth: ' + msg)
    return {}, 400, msg


  def License(self, node_id = None, node_api_key = None):
    post_data = {
      'api_key': node_api_key,
      'node_id': node_id
    }
    response, code, msg = self.APICall(api = app_config.NODE_LICENSE, post_data = post_data)
    self.logger.debug('[NodeManager] License: response ' + str(response))
    if code == 200:
      node_data = response.get('node_data')
      self.logger.debug('[NodeManager] License: Node data ' + str(node_data))
      response['node_data'] = node_data
      if node_data:
        self.logger.info('[NodeManager] License: OK')
        return response, 200, 'OK'
      else:
        msg = 'Node data is not found'
      code = 400
    return response, code, msg


  def Activate(self, node_api_key = None):
    post_data = {
      'api_key': node_api_key,
      'node_type': app_config.NODE_TYPE,
      'hostdata': _ToolSet.HostDataGet()
    }
    self.logger.debug('[NodeManager] Activate: post_data ' + str(post_data))
    response, code, msg = self.APICall(api = app_config.NODE_ACTIVATE, post_data = post_data)
    self.logger.debug('[NodeManager] Activate: response ' + str(response))
    if code == 200:
      node_data = response.get('node_data')
      self.logger.debug('[NodeManager] Activate: Node data ' + str(node_data))
      if node_data:
        Settings.query.update({ 'node_id': node_data.get('id') })
        db_session.commit()
        self.logger.info('[NodeManager] Activate: OK')
        return response, code, 'OK'
      else:
        msg = 'Node data is not found'
    self.logger.error('[NodeManager] Activate: ' + msg)
    return response, code, msg


  def Deactivate(self, node_id = None, node_api_key = None):
    post_data = {
      'api_key': node_api_key,
      'node_id': node_id
    }
    response, code, msg = self.APICall(api = app_config.NODE_DEACTIVATE, post_data = post_data)
    if code == 200:
      # Remove Node id
      Settings.query.update({ 'node_api_key': None })
      db_session.commit()
      self.logger.info('[NodeManager] Deactivate: OK')
    return response, code, msg


  def Service(self, service = None, request = None):
    response = {}
    msg = ''
    try:
      # WAN connection check
      #www_available, msg = _ToolSet.WANCheck()
      #if www_available:
      query_settings = Settings.query.first()
      node_id = query_settings.node_id
      node_api_key = query_settings.node_api_key
      if service == 'auth':
        return self.Auth(request = request, node_api_key = node_api_key)
      if service == 'activate':
        return self.Activate(node_api_key = node_api_key)
      if service == 'deactivate':
        return self.Deactivate(node_id = node_id, node_api_key = node_api_key)
      if service == 'license':
        return self.License(node_id = node_id, node_api_key = node_api_key)
    except:
      msg = 'Service exception error'
      raise
    self.logger.error('[NodeManager] Service: ' + msg)
    return response, 400, msg

