
import hashlib, time

from main.tools import _JSONTools, _AlarmManager
from main.job import _JobManager
from main.common.models import Job, Profile, Target, Server
from main.common.database import db_session
from main.common.log import LogManager


class ServerManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Server proto
  def ServerProto(self, json_data = {}):
    keys = ('ip', 'name', 'rtmp_srv', 'hls_srv')
    server = {}
    server.update({ key: json_data.get(key) for key in keys if key in json_data})
    return server


  def ServerList(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data)
      if json_check:
        #self.logger.debug('[ServerManager] List request: ' + str(json_data))
        query_server = Server.query.all()
        server_list = [ srv.serialize for srv in query_server ]
        hash_local = hashlib.md5(str(server_list).encode('utf-8')).hexdigest()
        response['hash'] = hash_local
        hash_remote = json_data.get('hash')
        if hash_remote == hash_local:
          response['server_list'] = []
        else:
          response['server_list'] = server_list
        return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[ServerManager] List: ' + msg)
    return response, 400, msg


  def ServerAdd(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'ip', 'name' ])
      if json_check:
        self.logger.debug('[ServerManager] ServerAdd request: ' + str(json_data))
        server_proto = self.ServerProto(json_data)
        self.logger.debug('[UserManager] ServerAdd server_proto: ' + str(server_proto))
        server = Server(**server_proto)
        db_session.add(server)
        db_session.commit()
        report = {
          'event': 'Server add',
          'info': _JSONTools.JSONToString(json_data = server_proto)[:-2]
        }
        _AlarmManager.OnAction(report)
        response.update({ 'server_id': server.id })
        self.logger.info('[ServerManager] ServerAdd: OK')
        return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[ServerManager] ServerAdd: ' + msg)
    return response, 400, msg


  def ServerUpdate(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id', 'ip', 'name' ])
      if json_check:
        self.logger.debug('[ServerManager] ServerUpdate request: ' + str(json_data))
        srv_id = str(json_data.get('id'))
        query_server = Server.query.filter_by(id = srv_id).first()
        if query_server:
          srv_types = []
          if query_server.rtmp_srv != json_data.get('rtmp_srv'): srv_types.append('RTMP')
          if query_server.hls_srv != json_data.get('hls_srv'): srv_types.append('HLS')
          self.logger.debug('[ServerManager] ServerUpdate Types: ' + str(srv_types))
          server_jobs = []
          if json_data.get('jobs_restart'):
            query_job = Job.query.join(Job.profile, Profile.target).filter(Job.run_status != 'OFF', Target.stream_srv == srv_id, Target.stream_type.in_(srv_types)).all()
            if query_job:
              for job in query_job:
                server_jobs.append(job.id)
              if server_jobs:
                # Stop associated server's jobs
                _JobManager.JobStop(json_data = { 'id': server_jobs })
          server_proto = self.ServerProto(json_data)
          self.logger.debug('[UserManager] ServerUpdate server_proto: ' + str(server_proto))
          # Apply server update to DB
          Server.query.filter_by(id = srv_id).update(server_proto)
          db_session.commit()
          self.logger.info('[ServerManager] ServerUpdate: ID ' + srv_id + ' updated')
          if server_jobs:
            _JobManager.JobStart(json_data = { 'id': server_jobs })
            self.logger.info('[ServerManager] ServerUpdate: Associated active jobs were restarted ' + str(server_jobs))
          report = {
            'event': 'Server update',
            'info': _JSONTools.JSONToString(json_data = server_proto)[:-2]
          }
          _AlarmManager.OnAction(report)
          self.logger.info('[ServerManager] ServerUpdate: OK')
          return response, 200, 'OK'
        else:
          msg = 'Server ID is not found'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[ServerManager] ServerUpdate: ' + msg)
    return response, 400, msg


  def ServerDelete(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      if json_check:
        self.logger.debug('[ServerManager] ServerDelete request: ' + str(json_data))
        srv_id = str(json_data.get('id'))
        query_server = Server.query.filter_by(id = srv_id).first()
        if query_server:
          # Select server's jobs
          query_job = Job.query.join(Job.profile, Profile.target).filter(Target.stream_srv == srv_id).all()
          if query_job:
            server_jobs = []
            # TODO: Optimize DB query to get only Job IDs with 'entities'
            for job in query_job:
              server_jobs.append(job.id)
            if server_jobs:
              # Stop associated server's jobs
              _JobManager.JobStop(json_data = { 'id': server_jobs })
              self.logger.info('[ServerManager] ServerDelete: Associated jobs were stopped ' + str(server_jobs))
          # Delete server record from DB
          db_session.delete(query_server)
          db_session.commit()
          self.logger.info('[ServerManager] ServerDelete: ID ' + srv_id + ' deleted')
          report = {
            'event': 'Server delete',
            'info': 'ID: ' + srv_id + ', Name: ' + str(query_server.name) + ', IP: ' + str(query_server.ip)
          }
          _AlarmManager.OnAction(report)
          self.logger.info('[ServerManager] ServerDelete: OK')
          return response, 200, 'OK'
        else:
          msg = 'Server ID is not found'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[ServerManager] ServerDelete: ' + msg)
    return response, 400, msg

