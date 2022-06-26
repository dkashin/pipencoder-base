
import time

from main.tools import _AlarmManager, _JSONTools, _FileTools
from main.job import _JobManager
from main.common.config import app_config
from main.common.models import Job, Settings
from main.common.database import db_session
from main.common.log import LogManager


class SettingsManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Load settings
  def SettingsLoad(self, request = None, json_data = None):
    response = {}
    try:
      response_data = {
        'settings': Settings.query.first().serialize,
        'media': {
          'images': _FileTools.ListDir(dir = app_config.IMAGES_DIR),
          'clips': _FileTools.ListDir(dir = app_config.CLIPS_DIR)
        }
      }
      response.update(response_data)
      self.logger.debug('[SettingsManager] Load: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SettingsManager] Load: ' + msg)
    return response, 400, msg


  # Save settings
  def SettingsSave(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'default_fail_type', 'default_fail_src' ])
      if json_check:
        self.logger.debug('[SettingsManager] Save request: ' + str(json_data))
        json_data.pop('version', None)
        json_data.pop('api_key', None)
        set_id = json_data.get('id')
        query = Settings.query.filter_by(id = set_id).first()
        if query:
          active_job_counter = []
          if query.default_fail_src != json_data.get('default_fail_src'):
            query_job = Job.query.filter(Job.source_active == 'failover', Job.run_status != 'OFF').all()
            if query_job:
              for job in query_job:
                active_job_counter.append(job.id)
              if active_job_counter:
                # Stop active server's jobs
                _JobManager.JobStop(json_data = { 'id': active_job_counter })
          Settings.query.filter_by(id = set_id).update(json_data)
          db_session.commit()
          self.logger.info('[SettingsManager] Save: OK')
          if active_job_counter:
            _JobManager.JobStart(json_data = { 'id': active_job_counter })
            self.logger.info('[SettingsManager] Default Failover update: Associated active jobs were restarted ' + str(active_job_counter))
          info = _JSONTools.JSONToString(json_data = json_data)
          _AlarmManager.OnAction(report = { 'event': 'Save settings', 'info': info[:-2] })
          return response, 200, 'OK'
        else:
          msg = 'Settings query error'
    except:
      msg = 'Exception error'
      #raise
    self.logger.error('[SettingsManager] Save: ' + msg)
    return response, 400, msg

