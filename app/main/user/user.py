
import time

from main.tools import _JSONTools, _AlarmManager
from main.common.database import db_session
from main.common.extensions import bcrypt
from main.common.models import User
from main.common.log import LogManager


# User management
class UserManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # User proto
  def UserProto(self, json_data = {}):
    keys = ('username', 'password', 'admin', 'alias')
    user = {}
    user.update({ key: json_data.get(key) for key in keys if key in json_data})
    return user


  # List all users
  def UserList(self, request = None, json_data = None):
    response = {}
    try:
      query_user = User.query.filter_by(su = False).all()
      response.update({ 'users': [ user.serialize for user in query_user ] })
      self.logger.debug('[UserManager] UserList: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[UserManager] UserList: ' + msg)
    return response, 400, msg


  # User register
  def UserAdd(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'username', 'password' ])
      if json_check:
        self.logger.debug('[UserManager] UserAdd request: ' + str(json_data))
        user_proto = self.UserProto(json_data)
        self.logger.debug('[UserManager] UserAdd user_proto: ' + str(user_proto))
        user = User(**user_proto)
        try:
          db_session.add(user)
          db_session.commit()
          user_id = str(user.id)
          self.logger.info('[UserManager] UserAdd: Username ' + user.username + ' / ID ' + user_id)
          report = {
            'event': 'User add',
            'info': _JSONTools.JSONToString(json_data = user_proto)[:-2]
          }
          _AlarmManager.OnAction(report)
          response.update({ 'user_id': user_id })
          self.logger.info('[UserManager] UserAdd: OK')
          return response, 200, 'OK'
        except:
          msg = 'User name has already taken'
          #raise
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[UserManager] UserAdd: ' + msg)
    return response, 400, msg


  # User update
  def UserUpdate(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      if json_check:
        user_proto = self.UserProto(json_data)
        self.logger.debug('[UserManager] UserUpdate request: ' + str(json_data))
        user_id = str(json_data.get('id'))
        query = User.query.filter_by(id = user_id).first()
        if query:
          info = 'Username: ' + query.username
          username = json_data.get('username')
          if username != query.username:
            info +=  ' -> ' + username
          admin = json_data.get('admin')
          info += ', Admin: ' + str(admin)
          password_update = json_data.get('password')
          if password_update:
            json_data.update({
              'password': bcrypt.generate_password_hash(password_update)
            })
            info += ', Password has been changed'
          else:
            json_data.pop('password', None)
          try:
            user_proto = self.UserProto(json_data)
            self.logger.info('[UserManager] UserUpdate user_proto: ' + str(user_proto))
            User.query.filter_by(id = user_id).update(user_proto)
            db_session.commit()
            self.logger.info('[UserManager] UserUpdate: ' + info)
            report = {
              'event': 'User update',
              'info': info
            }
            _AlarmManager.OnAction(report)
            self.logger.info('[UserManager] UserUpdate: OK')
            return response, 200, 'OK'
          except:
            msg = 'User name has already taken'
            #raise
        else:
          msg = 'User is not found'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[UserManager] UserUpdate: ' + msg)
    return response, 400, msg


  # User delete
  def UserDelete(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      if json_check:
        self.logger.debug('[UserManager] UserDelete request: ' + str(json_data))
        user_id = str(json_data.get('id'))
        query = User.query.filter_by(id = user_id).first()
        if query:
          username = query.username
          db_session.delete(query)
          db_session.commit()
          self.logger.info('[UserManager] UserDelete: Username ' + username + ' / ID ' + user_id)
          report = {
            'event': 'User delete',
            'info': 'User name: ' + username
          }
          _AlarmManager.OnAction(report)
          self.logger.info('[UserManager] UserDelete: OK')
          return response, 200, 'OK'
        else:
          msg = 'User is not found'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[UserManager] UserDelete: ' + msg)
    return response, 400, msg

