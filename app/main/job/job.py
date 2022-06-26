
import os, time, json, hashlib

from datetime import datetime
from sqlalchemy import and_, or_, text, func

from main.common.config import app_config
from main.common.log import LogManager
from main.common.models import Job, Profile, Target, Server
from main.common.database import db_session
from main.tools import _FileTools, _JSONTools, _AlarmManager
from main.pipe import _MediaPipe
from main.node import _NodeManager


class JobManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


# TODO: Job pool control
#  def JobsPoolCheck(self, job_id = None):
#    from check.check import _JobsPool
#    self.logger.debug('[JobManager] _JobsPool: ' + str(_JobsPool))
#    result = False
#    try:
#      for job in _JobsPool:
#        if job['id'] == job_id:
#          #job['threads'].join()
#          self.logger.debug('[JobManager] JobsPoolCheck: Found match ' + str(job['id']))
#    except:
#      self.logger.debug('[JobManager] JobsPoolCheck: Job not found')
#    return result


  ### Mass job status update ###
  def JobStatusUpdate(self, query = None, data = {}):
    for q in query:
      Job.query.filter_by(id = q.id).update(data)
    db_session.commit()


  ### Parse Target data ###
  def TargetParse(self, profile = None):
    targets = []
    try:
      for t_counter, target in enumerate(profile['target']):
        json_check, msg, json_data = _JSONTools.CheckIntegrity(json_data = target, match_keys = [ 'target_type', 'stream_type', 'stream_srv' ])
        json_check_protocol = []
        if json_check:
          if target['target_type'] == 'Stream':
            if target['stream_type'] == 'HLS':
              json_check_protocol = [ 'stream_name', 'hls_list_name' ]
            elif target['stream_type'] == 'RTMP':
              json_check_protocol = [ 'stream_name', 'stream_app' ]
            elif target['stream_type'] == 'UDP':
              json_check_protocol = [ 'udp_ip', 'udp_port' ]
            elif target['stream_type'] == 'SRT':
              json_check_protocol = [ 'srt_ip', 'srt_port' ]
          if target['target_type'] == 'Device':
            json_check_protocol = [ 'device_name' ]
          json_check, msg, json_data = _JSONTools.CheckIntegrity(json_data = target, match_keys = json_check_protocol)
        if json_check:
          targets.append(Target(**target))
        else:
          msg = 'Target #' + str(t_counter) + ' (' + str(msg) + ')'
          break
    except:
      msg = 'Incorrect target data'
      self.logger.debug('[JobManager] TargetParse: Incorrect target data')
      raise
    return targets, msg


  ### Parse Profile data ###
  def ProfileParse(self, json_data = None):
    profiles = []
    try:
      for p_counter, profile in enumerate(json_data.get('profile')):
        json_check, msg, json_data = _JSONTools.CheckIntegrity(json_data = profile, match_keys = [ 'vpreset', 'apreset', 'target' ])
        if json_check:
          targets, msg = self.TargetParse(profile = profile)
          if targets:
            profile['target'] = targets
            profile = Profile(**profile)
            profiles.append(profile)
          else:
            break
        else:
          msg = 'Profile #' + str(p_counter) + ' (' + str(msg) + ')'
          break
    except:
      msg = 'Incorrect profile data'
      self.logger.debug('[JobManager] ProfileParse: Incorrect profile data')
      raise
    return profiles, msg


  ### Add new Job to database ###
  def JobDBAdd(self, json_data = None):
    job = None
    try:
      profiles, msg = self.ProfileParse(json_data = json_data)
      if profiles:
        job_data = json_data.get('job_data')
        job_data['profile'] = profiles
        job = Job(**job_data)
        db_session.add(job)
        db_session.commit()
        msg = 'OK'
    except:
      msg = 'Incorrect job data'
      self.logger.debug('[JobManager] JobDBAdd: Incorrect job data')
      #raise
    return job, msg


  ### Update Job database values ###
  def JobDBUpdate(self, json_data = None, job_query = None, job_run_allow = False, logger_job = None):
    result = False
    try:
      job_data = json_data.get('job_data')
      job_id = str(job_data['id'])
      profiles, msg = self.ProfileParse(json_data = json_data)
      if profiles:
        restart_processing = False
        try:
          if json_data.get('restart_required') and (job_query.run_status != 'OFF') and job_run_allow:
            logger_job.info('[JobManager] Update: Restart required')
            #self.JobsPoolCheck(job_id = job_id)
            Job.query.filter_by(id = job_id).update({ 'run_status': 'UPD', 'start_time': datetime.now(), 'uptime': None, 'retries': 0, 'sys_stats': {} })
            db_session.commit()
            _MediaPipe.Init(query = job_query, logger = logger_job)
            _MediaPipe.EncoderStop()
            restart_processing = True
        except:
          self.logger.debug('[JobManager] JobDBUpdate: Restart failed exception')
          raise
        profile_query = Profile.query.filter_by(parent_id = job_id).all()
        for pq in profile_query:
          db_session.delete(pq)
        job_query.profile = profiles
        Job.query.filter_by(id = job_id).update(job_data)
        db_session.commit()
        if restart_processing:
          _MediaPipe.Init(query = job_query, logger = logger_job)
          _MediaPipe.EncoderStart()
        result = True
        msg = 'OK'
    except:
      msg = 'Incorrect job data'
      self.logger.debug('[JobManager] JobDBUpdate: Incorrect job data')
#      raise
    return result, msg


  def TargetURLPreview(self, query = None, q_serial = None):
    profiles_all = query.profile.all()
    for p_key, profile in enumerate(profiles_all):
      targets_all = profile.target.all()
      for t_key, target in enumerate(targets_all):
        if target.target_type == 'Stream':
          server = Server.query.filter_by(id = target.stream_srv).first()
          if server:
            if target.stream_type == 'RTMP':
              preview = os.path.join(server.rtmp_srv, target.stream_app, target.stream_name)
            elif target.stream_type == 'UDP':
              preview = 'udp://' + target.udp_ip + ':' + str(target.udp_port)
            elif target.stream_type == 'SRT':
              preview = 'srt://' + target.srt_ip + ':' + str(target.srt_port)
            elif target.stream_type == 'HLS':
              hls_abr_basename = ''
              if query.hls_abr_basename and query.hls_abr_active:
                hls_abr_basename = query.hls_abr_basename
              manifest_name = target.hls_list_name + app_config.HLS_MANIFEST_EXT
              preview = os.path.join(server.hls_srv, hls_abr_basename, target.stream_name, manifest_name)
          else:
            preview = 'Preview is not available'
        elif target.target_type == 'Device':
          preview = target.device_name or 'Preview is not available'
        else:
          preview = 'Preview is not available'
        q_serial['profile'][p_key]['target'][t_key]['preview'] = preview
    if query.hls_abr_active:
      abr_server = Server.query.filter_by(id = query.hls_abr_server).first()
      if abr_server:
        abr_manifest_name = str(query.hls_abr_list_name) + app_config.HLS_MANIFEST_EXT
        hls_abr_url = os.path.join(str(abr_server.hls_srv), str(query.hls_abr_basename), str(abr_manifest_name))
        q_serial['job_data']['hls_abr_url'] = hls_abr_url
    else:
      q_serial['job_data']['hls_abr_url'] = 'Preview is not available'
    return q_serial


  def JobListDBFields(self, field_type = 'job'):
    fields = []
    if field_type == 'job':
      fields = [ 'id', 'sid', 'job_name', 'source_main', 'source_main_type', 'source_bak', 'source_bak_type', 'source_fail', 'source_fail_type', 'source_active', 'hls_drm_active', 'hls_abr_active', 'hls_abr_list_name', 'hls_abr_basename', 'run_status', 'retries', 'start_time', 'uptime' ]
    if field_type == 'profile':
      fields = [ 'main_vpid', 'main_apid', 'main_dpid', 'bak_vpid', 'bak_apid', 'bak_dpid', 'fail_vpid', 'fail_apid', 'fail_dpid', 'vpreset', 'apreset', 'nvenc_gpu', 'venc_di', 'venc_psize' ]
    if field_type == 'target':
      fields = [ 'stream_srv', 'stream_type', 'stream_name', 'stream_app', 'hls_abr_asset', 'hls_list_name', 'hls_seg_name', 'udp_ip', 'udp_port' ]
    if field_type == 'source_global':
      fields = [ 'source_main', 'source_bak', 'source_fail' ]
    if field_type == 'target_global':
      fields = [ 'stream_name', 'stream_app', 'hls_list_name', 'hls_seg_name', 'udp_ip', 'udp_port' ]
    if field_type == 'video_pid_global':
      fields = [ 'main_vpid', 'bak_vpid', 'fail_vpid' ]
    if field_type == 'audio_pid_global':
      fields = [ 'main_apid', 'bak_apid', 'fail_apid' ]
    if field_type == 'data_pid_global':
      fields = [ 'main_dpid', 'bak_dpid', 'fail_dpid' ]
    return fields


  def JobListFilter(self, filters = []):
    db_filter_and = []
    db_filter_or = []
    if filters:
      for filter_ in filters:
        f_field = filter_['field']
        f_value = str(filter_['value'])
        f_type = filter_['type']
        if filter_['value']:
          if f_field == 'source_global':
            for field in self.JobListDBFields(f_field):
              like = text('"Job".' + field + ' LIKE "%' + f_value + '%"')
              db_filter_or.append(like)
              #self.logger.debug('[JobManager] Like source_global: ' + str(like))
          elif f_field == 'target_global':
            for field in self.JobListDBFields(f_field):
              like = text('"Target".' + field + ' LIKE "%' + f_value + '%"')
              db_filter_or.append(like)
              #self.logger.debug('[JobManager] Like target_global: ' + str(like))
          elif f_field in ['video_pid_global', 'audio_pid_global', 'data_pid_global']:
            for field in self.JobListDBFields(f_field):
              like = text('"Profile".' + field + ' LIKE "%' + f_value + '%"')
              db_filter_or.append(like)
              #self.logger.debug('[JobManager] Like ' + str(f_field) + ': ' + str(like))
          else:
            if f_field in self.JobListDBFields('job'):
              like = text('"Job".' + f_field + ' LIKE "%' + f_value + '%"')
              #self.logger.debug('[JobManager] Like ' + str(f_field) + ': ' + str(like))
            elif f_field in self.JobListDBFields('profile'):
              like = text('"Profile".' + f_field + ' LIKE "%' + f_value + '%"')
              #self.logger.debug('[JobManager] Like ' + str(f_field) + ': ' + str(like))
            elif f_field in self.JobListDBFields('target'):
              like = text('"Target".' + f_field + ' LIKE "%' + f_value + '%"')
              #self.logger.debug('[JobManager] Like ' + str(f_field) + ': ' + str(like))
            else:
              like = ''
              #self.logger.warning('[JobManager] List: Filter is not applied (filter: ' + f_field + ', value: ' + f_value + ')')
            if str(like):
              if f_type == 'and':
                db_filter_and.append(like)
              else:
                db_filter_or.append(like)
        #else:
          #self.logger.warning('[JobManager] List: Filter value is empty for "' + f_field + '"')
    return db_filter_and, db_filter_or


  def JobListOrderBy(self, json_data):
    db_order_by = []
    sort_by = json_data.get('sort_by')
    sort_by_order = json_data.get('sort_by_order')
    if sort_by and (sort_by_order in [ 'asc', 'desc' ]):
      if sort_by in self.JobListDBFields('job'):
        order = text('Job.' + sort_by + ' ' + sort_by_order)
      elif sort_by in self.JobListDBFields('profile'):
        order = text('Profile.' + sort_by + ' ' + sort_by_order)
      elif sort_by in self.JobListDBFields('target'):
        order = text('Target.' + sort_by + ' ' + sort_by_order)
      else:
        order = ''
        #self.logger.warning('[JobManager] List sort-by is not applied (' + sort_by + ': ' + sort_by_order + ')')
      db_order_by.append(order)
      #self.logger.debug('[JobManager] List sort-by: ' + str(order))
    #else:
      #self.logger.warning('[JobManager] List sort-by is not applied (' + sort_by + ': ' + sort_by_order + ')')
    return db_order_by


  def JobListSerialize(self, query = None, hash_remote = None, response = {}):
    job_list = []
    var = {}
    for q in query:
      var[q.id] = { 'stats': q.sys_stats }
      ss_filename = q.id + '.jpg'
      ss_local = os.path.join(app_config.SS_DIR_SYS, ss_filename)
      ss_remote = os.path.join(app_config.SS_DIR_WEB, ss_filename)
      if _FileTools.HasExpired(file = ss_local, expire_time = 120, remove_expired = True):
        var[q.id]['ss'] = None
      else:
        timer = str(int(os.path.getmtime(ss_local)))
        var[q.id]['ss'] = ss_remote + '?' + timer
      q_serial = self.TargetURLPreview(query = q, q_serial = q.serialize)
      job_list.append(q_serial)
    response['var'] = var
    hash_local = hashlib.md5(str(job_list).encode('utf-8')).hexdigest()
    response['hash'] = hash_local
    if hash_remote == hash_local:
      response['job_list'] = []
    else:
      response['job_list'] = job_list
      #self.logger.debug('[JobManager] List: Hash has changed, Job list updating')
    return response


  def JobListDefaults(self, json_data):
    defaults = {
      'filters': [],
      'sort_by': 'sid',
      'sort_by_order': 'asc',
      'per_page': 50,
      'act_page': 1,
      'hash': None
    }
    for default in defaults:
      if not default in list(json_data.keys()):
        json_data[default] = defaults[default]
    return json_data


  def JobList(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data)
      if json_check:
        json_data = self.JobListDefaults(json_data)
        db_filter_and, db_filter_or = self.JobListFilter(json_data.get('filters'))
        if db_filter_and or db_filter_or:
          response['filtered'] = True
        db_order_by = self.JobListOrderBy(json_data)
        query = Job.query.join(Job.profile, Profile.target).filter(and_(*db_filter_and), or_(*db_filter_or)).order_by(*db_order_by).group_by(Job.id)
        jobs_total = Job.query.with_entities(func.count(Job.id)).scalar()
        response['jobs_total'] = jobs_total
        per_page = json_data.get('per_page')
        if per_page:
          query = query.limit(per_page)
        act_page = json_data.get('act_page')
        if act_page and per_page:
          query = query.offset((act_page - 1) * per_page)
        response = self.JobListSerialize(query = query, hash_remote = json_data.get('hash'), response = response)
        return response, 200, 'OK'
    except:
      msg = 'Exception error'
      #raise
    self.logger.error('[JobManager] List: ' + msg)
    return response, 400, msg


  def JobStatus(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      if json_check:
        self.logger.debug('[JobManager] JobStatus request: ' + str(json_data))
        job_id_list = json_data.get('id')
        if job_id_list:
          query = Job.query.filter(Job.id.in_(job_id_list)).all()
        else:
          job_id_list = '(ALL)'
          query = Job.query.all()
        if query:
          response['data'] = []
          for q in query:
            response['data'].append({ 'id': q.id, 'status': q.run_status })
          self.logger.info('[JobManager] Status: OK ' + str(job_id_list))
          return response, 200, 'OK'
        else:
          msg = 'No job(s) to process'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Status: ' + msg)
    return response, 400, msg


  def JobLicenseLimits(self, job_id_list = []):
    check_passed = False
    limits = {
      'auth': { 'result': False, 'msg': '' },
      'job_run_allow': { 'result': False, 'msg': '' },
      'job_add_allow': { 'result': False, 'msg': '' }
    }
    try:
      response, code, msg = _NodeManager.Service(service = 'license')
      self.logger.debug('[JobManager] JobLicenseLimits response: ' + str(response))
      self.logger.debug('[JobManager] JobLicenseLimits code: ' + str(code) + ', msg: ' + str(msg))
      if code == 200:
        limits['auth']['result'] = True
        jobs_total = Job.query.with_entities(func.count(Job.id)).scalar()
        limit_jobs_total = response['node_data']['limit_jobs_total']
        self.logger.debug('[JobManager] JobLicenseLimits jobs_total: ' + str(jobs_total))
        self.logger.debug('[JobManager] JobLicenseLimits limit_jobs_total: ' + str(limit_jobs_total))
        if jobs_total < limit_jobs_total or limit_jobs_total == -1:
          limits['job_add_allow'] = { 'result': True, 'msg': 'OK' }
        else:
          limits['job_add_allow']['msg'] = 'License limits exceed (' + str(limit_jobs_total) + ' total job(s))'
        if job_id_list:
          jobs_active_total = Job.query.filter(Job.run_status != 'OFF').with_entities(func.count(Job.id)).scalar()
          self.logger.debug('[JobManager] JobLicenseLimits jobs_active_total: ' + str(jobs_active_total))
          jobs_active_id_list = Job.query.filter(Job.id.in_(job_id_list), Job.run_status != 'OFF').with_entities(func.count(Job.id)).scalar()
          self.logger.debug('[JobManager] JobLicenseLimits jobs_active_id_list: ' + str(jobs_active_id_list))
          jobs_active_new = jobs_active_total - jobs_active_id_list
          self.logger.debug('[JobManager] JobLicenseLimits jobs_active_new: ' + str(jobs_active_new))
          if jobs_active_new:
            jobs_to_process = jobs_active_total + jobs_active_new
          else:
            jobs_to_process = len(job_id_list)
        else:
          jobs_to_process = jobs_total
        self.logger.debug('[JobManager] JobLicenseLimits jobs_to_process: ' + str(jobs_to_process))
        limit_jobs_active = response['node_data']['limit_jobs_active']
        self.logger.debug('[JobManager] JobLicenseLimits limit_jobs_active: ' + str(limit_jobs_active))
        if jobs_to_process <= limit_jobs_active or limit_jobs_active == -1:
          limits['job_run_allow'] = { 'result': True, 'msg': 'OK' }
          job_run_allow = True
        else:
          limits['job_run_allow']['msg'] = 'License limits exceed (' + str(limit_jobs_active) + ' active job(s))'
        check_passed = True
      else:
        error_msg = 'License: ' + msg
    except:
      error_msg = 'JobLicenseLimits exception'
      raise
    if not check_passed:
      limits['auth']['msg'] = error_msg
      limits['job_run_allow']['msg'] = error_msg
      limits['job_add_allow']['msg'] = error_msg
    return limits


  def JobStart(self, request = None, json_data = None):
    response = {}
    job_id_list = []
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      self.logger.debug('[JobManager] JobStart request: ' + str(json_data))
      if json_check:
        job_id_list = json_data.get('id')
        limits = self.JobLicenseLimits(job_id_list = job_id_list)
        msg = limits['job_run_allow']['msg']
        if limits['job_run_allow']['result']:
          if job_id_list:
            query = Job.query.filter(Job.id.in_(job_id_list), Job.run_status == 'OFF').order_by(Job.id.asc()).all()
            if query:
              update_data = { 'run_status': 'UPD', 'start_time': datetime.now(), 'uptime': None, 'retries': 0, 'sys_stats': {} }
              self.JobStatusUpdate(query = query, data = update_data)
              count = int(len(query)) - 1
              for idx, q in enumerate(query):
                logger_job = self.JobLogOpen(job_id = q.id)
                _MediaPipe.Init(query = q, logger = logger_job)
                _MediaPipe.EncoderStart()
                logger_job.info('[JobManager] Start: OK')
                report = { 'time': time.strftime('%x %X'), 'event': 'Job start', 'id': q.id, 'sid': q.sid, 'name': q.job_name, 'info': '-' }
                if idx == count:
                  _AlarmManager.OnAction(report = report)
                else:
                  _AlarmManager.OnAction(report = report, append = True)
              self.logger.info('[JobManager] Start: OK ' + str(job_id_list))
              return response, 200, 'OK'
            else:
              msg = 'No job(s) to process'
          else:
            job_id_list = '(ALL)'
            Job.query.filter_by(run_status = 'OFF').update({ 'run_status': 'UPD', 'start_time': datetime.now(), 'uptime': None, 'retries': 0, 'sys_stats': {} })
            db_session.commit()
            report = { 'time': time.strftime('%x %X'), 'event': 'Job start (ALL)', 'info': '-' }
            _AlarmManager.OnAction(report = report)
            self.logger.info('[JobManager] Start: OK ' + str(job_id_list))
            return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Start: ' + msg)
    return response, 400, msg


  def JobStop(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      self.logger.debug('[JobManager] JobStop request: ' + str(json_data))
      if json_check:
        job_id_list = json_data.get('id')
        if job_id_list:
          query = Job.query.filter(Job.id.in_(job_id_list)).order_by(Job.id.asc()).all()
          process_all = False
        else:
          job_id_list = '(ALL)'
          process_all = True
          query = Job.query.order_by(Job.sid.asc()).all()
        if query:
          update_data = { 'run_status': 'OFF', 'start_time': datetime.now(), 'uptime': None, 'retries': 0, 'sys_stats': {} }
          self.JobStatusUpdate(query = query, data = update_data)
          count = int(len(query)) - 1
          for idx, q in enumerate(query):
            logger_job = self.JobLogOpen(job_id = q.id)
            _MediaPipe.Init(query = q, logger = logger_job)
            logger_job.info('[JobManager] Stop processing')
            _MediaPipe.EncoderStop()
            logger_job.info('[JobManager] Stopped')
            if not process_all:
              report = { 'time': time.strftime('%x %X'), 'event': 'Job stop', 'id': q.id, 'sid': q.sid, 'name': q.job_name, 'info': '-' }
              if idx == count:
                _AlarmManager.OnAction(report = report)
              else:
                _AlarmManager.OnAction(report = report, append = True)
          if process_all:
            report = { 'time': time.strftime('%x %X'), 'event': 'Job stop (ALL)', 'info': '-' }
            _AlarmManager.OnAction(report = report)
          self.logger.info('[JobManager] Stop: OK ' + str(job_id_list))
          return response, 200, 'OK'
        else:
          msg = 'No job(s) to process'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Stop: ' + msg)
    return response, 400, msg


  def JobRestart(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      self.logger.debug('[JobManager] JobRestart request: ' + str(json_data))
      if json_check:
        job_id_list = json_data.get('id')
        limits = self.JobLicenseLimits(job_id_list = job_id_list)
        msg = limits['job_run_allow']['msg']
        if limits['job_run_allow']['result']:
          if job_id_list:
            query = Job.query.filter(Job.id.in_(job_id_list)).order_by(Job.id.asc()).all()
            process_all = False
          else:
            job_id_list = '(ALL)'
            process_all = True
            query = Job.query.order_by(Job.sid.asc()).all()
          if query:
            update_data = { 'run_status': 'UPD', 'start_time': datetime.now(), 'uptime': None, 'retries': 0, 'sys_stats': {} }
            self.JobStatusUpdate(query = query, data = update_data)
            count = int(len(query)) - 1
            for idx, q in enumerate(query):
              logger_job = self.JobLogOpen(job_id = q.id)
              _MediaPipe.Init(query = q, logger = logger_job)
              logger_job.info('[JobManager] Restart processing')
              _MediaPipe.EncoderStop()
              _MediaPipe.EncoderStart()
              logger_job.info('[JobManager] Restart: OK')
              if not process_all:
                report = { 'time': time.strftime('%x %X'), 'event': 'Job restart', 'id': q.id, 'sid': q.sid, 'name': q.job_name, 'info': '-' }
                if idx == count:
                  _AlarmManager.OnAction(report = report)
                else:
                  _AlarmManager.OnAction(report = report, append = True)
            if process_all:
              report = { 'time': time.strftime('%x %X'), 'event': 'Job restart (ALL)', 'info': '-' }
              _AlarmManager.OnAction(report = report)
            self.logger.info('[JobManager] Restart: OK ' + str(job_id_list))
            return response, 200, 'OK'
          else:
            msg = 'No job(s) to process'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Restart: ' + msg)
    return response, 400, msg


  def JobAdd(self, request = None, json_data = None):
    response = {}
    try:
      limits = self.JobLicenseLimits(job_id_list = [1])
      msg = limits['job_add_allow']['msg']
      if limits['job_add_allow']['result']:
        self.logger.debug('[JobManager] JobAdd request: ' + str(request.get_json() if request else json_data))
        json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'job_data', 'profile', 'job_start' ])
        if json_check:
          job, msg = self.JobDBAdd(json_data = json_data)
          if job:
            logger_job = self.JobLogOpen(job_id = job.id)
            logger_job.info('[JobManager] Add: OK')
            self.logger.info('[JobManager] Add: OK (ID: ' + str(job.id) + ')')
            response['job_id'] = job.id
            if json_data.get('job_start'):
              if limits['job_run_allow']['result']:
                job.run_status = 'UPD'
                job.start_time = datetime.now()
                db_session.commit()
                logger_job.info('[JobManager] Start: OK')
            report = { 'time': time.strftime('%x %X'), 'event': 'Job add', 'id': job.id, 'sid': job.sid, 'name': job.job_name, 'info': '-' }
            _AlarmManager.OnAction(report = report)
            return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Add: ' + msg)
    return response, 400, msg


  def JobUpdate(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'job_data', 'profile', 'restart_required' ])
      self.logger.debug('[JobManager] JobUpdate request: ' + str(json_data))
      if json_check:
        job_data = json_data.get('job_data')
        if 'id' in list(job_data.keys()):
          job_id = str(job_data['id'])
          limits = self.JobLicenseLimits(job_id_list = [ job_id ])
          msg = limits['auth']['msg']
          if limits['auth']['result']:
            query = Job.query.filter_by(id = job_id).first()
            if query:
              logger_job = self.JobLogOpen(job_id = job_id)
              result, msg = self.JobDBUpdate(json_data, query, limits['job_run_allow']['result'], logger_job)
              if result:
                logger_job.info('[JobManager] Updated')
                self.logger.info('[JobManager] Update: OK (ID: ' + str(job_id) + ')')
                info = _JSONTools.JSONToString(json_data = json_data)
                report = { 'time': time.strftime('%x %X'), 'event': 'Job update', 'id': job_id, 'sid': query.sid, 'name': query.job_name, 'info': info[:-2] }
                _AlarmManager.OnAction(report = report)
                return response, 200, 'OK'
            else:
              msg = 'No job(s) to process'
        else:
          msg = 'Required key: id'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Update: ' + msg)
    return response, 400, msg


  def JobDelete(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'id' ])
      self.logger.debug('[JobManager] JobDelete request: ' + str(json_data))
      if json_check:
        job_id_list = json_data.get('id')
        query = Job.query.filter(Job.id.in_(job_id_list)).all()
        if query:
          count = len(query)
          for idx, q in enumerate(query):
            _MediaPipe.Init(query = q)
#            _MediaPipe.EncoderStop(wipe_logs = False)
            _MediaPipe.EncoderStop(wipe_logs = True)
            report = { 'time': time.strftime('%x %X'), 'event': 'Job delete', 'id': q.id, 'sid': q.sid, 'name': q.job_name, 'info': '-' }
            db_session.delete(q)
            db_session.commit()
            self.logger.info('[JobManager] Delete: OK ' + str(job_id_list))
            if idx == count:
              _AlarmManager.OnAction(report = report)
            else:
              _AlarmManager.OnAction(report = report, append = True)
          return response, 200, 'OK'
        else:
          msg = 'No job(s) to process'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[JobManager] Delete: ' + msg)
    return response, 400, msg

