
import hashlib, uuid, base64

from flask_login import login_user, logout_user, current_user

from datetime import datetime, timedelta
from sqlalchemy import func

from main.tools import _JSONTools
from main.common.log import LogManager
from main.common.models import User, APIKey
from main.common.database import db_session
from main.common.extensions import bcrypt


# Auth management
class AuthManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # API request key check
  def APIKeyCheck(self, request = None, json_data = None):
    try:
      # HTTP header API key
      api_key = request.headers.get("X-API-KEY")
      try:
        api_key = base64.b64decode(api_key)
      except:
        pass
      if not api_key:
        # JSON request API key
        json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'api_key' ])
        if json_check:
          api_key = json_data.get('api_key')
      if api_key:
        api_key_hash = hashlib.sha256(str(api_key).encode('utf-8')).hexdigest()
        api_key_query = APIKey.query.filter_by(key = api_key_hash).first()
        if api_key_query:
          if api_key_query.expire > datetime.now() or api_key_query.expire == datetime.max:
            user = User.query.filter_by(username = api_key_query.username).first()
            return user
          else:
            db_session.delete(api_key_query)
            db_session.commit()
            msg = 'Key has expired so removed'
        else:
          msg = 'Key is not found'
      else:
        msg = 'Request has no API key'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[AuthManager] APIKeyCheck: ' + msg)
    return None


  # API key generator
  def APIKeyGen(self, user = None, key_ttl = None):
    try:
      api_keys_len = user.api_keys.with_entities(func.count(APIKey.id)).scalar()
      self.logger.debug('[AuthManager] APIKeyGen: API keys used ' + str(api_keys_len))
      self.logger.debug('[AuthManager] APIKeyGen: API keys limit ' + str(user.api_keys_limit))
      if api_keys_len < user.api_keys_limit:
        self.logger.debug('[AuthManager] APIKeyGen: Generating new API key')
        new_api_key = { 'username': user.username }
        api_key = uuid.uuid4().hex
        if key_ttl:
          new_api_key['expire'] = datetime.now() + timedelta(seconds = key_ttl)
          self.logger.debug('[AuthManager] APIKeyGen: API key TTL is ' + str(key_ttl) + ' sec')
        self.logger.debug('[AuthManager] APIKeyGen: API key ' + str(api_key))
        new_api_key['key'] = hashlib.sha256(str(api_key).encode('utf-8')).hexdigest()
        new_api_key = APIKey(**new_api_key)
        db_session.add(new_api_key)
        return { 'api_key': api_key, 'expire': new_api_key.expire }
      else:
        msg = 'API keys limit has been reached (' + str(user.api_keys_limit) + ')'
    except:
      msg = 'Exception error'
      self.logger.error('[AuthManager] APIKeyGen: Exception error')
      raise
    return { 'msg': msg }


  # API key remove
  def APIKeyDelete(self, api_key = None, username = None, remove_all = False):
    self.logger.info('[AuthManager] APIKeyDelete: api_key ' + str(api_key))
    self.logger.info('[AuthManager] APIKeyDelete: username ' + str(username))
    if remove_all:
      APIKey.query.filter_by(username = username).delete()
      db_session.commit()
      msg = 'All API keys has been deleted'
    elif api_key:
      api_key_hash = hashlib.sha256(str(api_key).encode('utf-8')).hexdigest()
      self.logger.info('[AuthManager] APIKeyDelete: api_key_hash ' + str(api_key_hash))
      APIKey.query.filter_by(key = api_key_hash).delete()
      db_session.commit()
      msg = 'API key has been deleted'
    else:
      msg = 'No API key found'
    self.logger.info('[AuthManager] APIKeyDelete: ' + msg)
    return msg


  # API key actions
  def APIKeyAction(self, user = None, api_key_options = None):
    action = api_key_options.get('action')
    if action == 'create':
      key_ttl = api_key_options.get('key_ttl')
      msg = self.APIKeyGen(user = user, key_ttl = key_ttl)
    elif action == 'reset':
      msg = self.APIKeyDelete(username = user.username, remove_all = True)
    else:
      msg = 'API key options error'
    return msg


  # User login
  def Login(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'username', 'password' ])
      if json_check:
        self.logger.debug('[AuthManager] Login request: ' + str(json_data))
        user = User.query.filter_by(username = json_data.get('username')).first()
        if user:
          if bcrypt.check_password_hash(user.password, json_data.get('password')):
              user.last_login = datetime.now()
              api_key_options = json_data.get('api_key_options')
              if api_key_options:
                response.update({
                  'api_key_data': self.APIKeyAction(user = user, api_key_options = api_key_options)
                })
              db_session.commit()
              response_data = {
                'admin': user.admin,
                'last_login': user.last_login
              }
              response.update(response_data)
              login_user(user)
              self.logger.debug('[AuthManager] Login: ' + user.username + ' (admin: ' + str(user.admin) + ')')
              return response, 200, 'OK'
          else:
            msg = 'Invalid username and/or password'
        else:
          msg = 'Invalid username and/or password'
    except:
      db_session.rollback()
      msg = 'Exception error'
      raise
    self.logger.error('[AuthManager] Login: ' + msg)
    return response, 400, msg


  # User logout
  def Logout(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data)
      if json_check:
        self.logger.debug('[AuthManager] Logout request: ' + str(json_data))
        user = current_user.username if current_user else None
        api_key = json_data.get('api_key')
        self.APIKeyDelete(api_key = api_key, username = user)
        logout_user()
        self.logger.debug('[AuthManager] Logout: OK (' + user + ')')
        return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[AuthManager] Logout: ' + msg)
    return response, 400, msg

