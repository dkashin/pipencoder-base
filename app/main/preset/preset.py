
import os, time, json

from json.decoder import JSONDecodeError

from main.tools import _JSONTools, _FileTools, _AlarmManager
from main.job import _JobManager
from main.common.config import app_config
from main.common.models import Job, Profile
from main.common.log import LogManager


class PresetsManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Get presets list
  def PresetsList(self, request = None, json_data = None):
    response = {}
    try:
      preset_list = {
        'vpresets': _FileTools.ListDir(dir = app_config.VPRESETS_DIR),
        'apresets': _FileTools.ListDir(dir = app_config.APRESETS_DIR)
      }
      response.update(preset_list)
      self.logger.info('[PresetsManager] List: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[PresetsManager] List: ' + msg)
    return response, 400, msg


  ### Get presets data ###
  def PresetsData(self, request = None, json_data = None):
    response = {}
    try:
      vpresets = []
      for vp in _FileTools.ListDir(dir = app_config.VPRESETS_DIR):
        vp_path = os.path.join(app_config.VPRESETS_DIR, vp)
        with open(vp_path) as preset_data:
          try:
            preset_data = json.load(preset_data)
            preset_data['filename'] = vp
            vpresets.append(preset_data)
          except JSONDecodeError as e:
            self.logger.error(f'[PresetsManager] vPreset JSONDecodeError [{vp}]')
      if vpresets:
        response.update({
          'vpresets': sorted(vpresets, key = lambda x : x['name'], reverse = False)
        })
      apresets = []
      for ap in _FileTools.ListDir(dir = app_config.APRESETS_DIR):
        ap_path = os.path.join(app_config.APRESETS_DIR, ap)
        with open(ap_path) as preset_data:
          try:
            preset_data = json.load(preset_data)
            preset_data['filename'] = ap
            apresets.append(preset_data)
          except JSONDecodeError as e:
            self.logger.error(f'[PresetsManager] aPreset JSONDecodeError [{ap}]')
      if apresets:
        response.update({
          'apresets': sorted(apresets, key = lambda x : x['name'], reverse = False)
        })
      self.logger.debug('[PresetsManager] Data: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[PresetsManager] Data: ' + msg)
    return response, 400, msg


  ### Preset add ###
  def PresetAddUpdate(self, request = None, json_data = None, action = 'add'):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'preset_data', 'preset_type' ])
      if json_check:
        preset_data = json_data.get('preset_data')
        preset_type = json_data.get('preset_type')
        self.logger.info('[PresetsManager] ' + action + ' request: ' + str(json_data))
        json_check, msg, json_data = _JSONTools.CheckIntegrity(json_data = preset_data, match_keys = [ 'name' ])
        if json_check:
          preset_name = preset_data.get('name').replace(' ','_')
          filename = os.path.join(app_config.PRESETS_DIR, preset_type, preset_name)
          if (not os.path.isfile(filename)) or (action == 'update'):
            try:
              with open(filename, 'w') as preset_file:
                json.dump(preset_data, preset_file, indent = 2, sort_keys = True)
              if action == 'update':
                if preset_type == 'video':
                  query_job = Job.query.join(Job.profile).filter(Job.run_status != 'OFF', Profile.vpreset == preset_name).all()
                else:
                  query_job = Job.query.join(Job.profile).filter(Job.run_status != 'OFF', Profile.apreset == preset_name).all()
                active_job_counter = []
                if query_job:
                  for job in query_job:
                    active_job_counter.append(job.id)
                  if active_job_counter:
                    # Stop active server's jobs
                    _JobManager.JobStop(json_data = { 'id': active_job_counter })
                if active_job_counter:
                  _JobManager.JobStart(json_data = { 'id': active_job_counter })
                  self.logger.info('[PresetsManager] Update: Associated active jobs were restated ' + str(active_job_counter))
              info = _JSONTools.JSONToString(json_data = preset_data)
              _AlarmManager.OnAction(report = { 'event': 'AV Preset ' + action, 'info': info[:-2] })
              self.logger.info('[PresetsManager] ' + action + ': OK')
              return response, 200, 'OK'
            except FileNotFoundError:
              msg = f'Preset is not found: {os.path.join(preset_type, preset_name)}'
          else:
            msg = 'Preset name already exists'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[PresetsManager] ' + action + ': ' + msg)
    return response, 400, msg



  ### Preset delete ###
  def PresetDelete(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'preset_name', 'preset_type' ])
      if json_check:
        preset_type = json_data.get('preset_type')
        preset_name = json_data.get('preset_name')
        self.logger.info('[PresetsManager] PresetDelete request: ' + str(json_data))
        filename = os.path.join(app_config.PRESETS_DIR, preset_type, preset_name)
        if os.path.isfile(filename):
          if preset_type == 'video':
            query_job = Job.query.join(Job.profile).filter(Profile.vpreset == preset_name).all()
          else:
            query_job = Job.query.join(Job.profile).filter(Profile.apreset == preset_name).all()
          if query_job:
            stop_jobs = []
            for job in query_job:
              stop_jobs.append(job.id)
            if stop_jobs:
              # Stop active server's jobs
              _JobManager.JobStop(json_data = { 'id': stop_jobs })
              self.logger.info('[PresetsManager] Delete: Associated jobs were stopped ' + str(stop_jobs))
          # Delete preset file
          os.remove(filename)
          report = {
            'event': 'AV Preset delete',
            'info': 'Preset name: ' + preset_name + ', Preset type: ' + preset_type
          }
          _AlarmManager.OnAction(report = report)
          self.logger.info('[PresetsManager] Delete: OK')
          return response, 200, 'OK'
        else:
          msg = f'Preset is not found: {os.path.join(preset_type, preset_name)}'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[PresetsManager] Delete: ' + msg)
    return response, 400, msg

