

import time, os, json, shlex, requests, psutil, shutil, copy, streamlink

from requests.exceptions import RequestException
from subprocess import STDOUT, check_output, CalledProcessError
from datetime import datetime

from main.pipe.pipe import MediaPipe
from main.tools import _FileTools, _SystemTools, _AlarmManager
from main.common.config import app_config
from main.common.models import Job


### Checkers ###
class CheckTools(MediaPipe):


  def __init__(self, query = None, job_id = None, logger = None):
    self.logger = logger or self.LogNull()
    if query or job_id:
      self.Init(query = query, job_id = job_id, logger = logger)


  ### HTTP stream check ###
  def CheckHTTP(self, url = None, headers = None, user = None, password = None, timeout = 3):
    result = False
    #headers = { 'User-Agent' : 'Winamp/2.1', 'Icy-MetaData' : '1' }
    try:
      r = requests.get(url, headers = headers, auth = (user, password), timeout = timeout, stream = True)
      code = r.status_code
      if code >= 200 and code < 400:
        result = True
        msg = 'OK'
      else:
        msg = 'CheckHTTP: Check error (HTTP code ' + str(code) + ')'
    except RequestException as e:
      ### Icecast (HTTP) stream check ###
      if 'ICY 200 OK' in str(e):
        msg = 'CheckHTTP: Icecast stream found'
        code = 200
      else:
        msg = 'CheckHTTP: Exception error (' + str(e) + ')'
    except:
      msg = 'CheckHTTP: Exception error'
      raise
    return result, msg


  # Check Youtube URL expiration (UTC)
  def YTExpireDate(self, url = ''):
    expire_date = None
    try:
      if all(char in url for char in [ '?', '&', '=' ]):
        url_split = url.split('?')
        url_split = url_split[1].split('&')
        for val in url_split:
          val = val.split('=')
          if val[0] == 'expire':
            expire_date = val[1]
            break
      else:
        url_split = url.split('/')
        value = 'expire'
        expire_date = url_split[ url_split.index(value) + 1 ] if value in url_split else None
    except:
      self.logger.error('[CheckTools] YTExpireDate exception error')
      raise
    return expire_date


  # Check Youtube links
  def YTDataToJSON(self, dict_data = None):
    json_data = {}
    try:
      if dict_data:
        programs = []
        for format_id, stream in list(dict_data.items()):
          if not format_id in [ 'best', 'worst' ]:
            stream_info, msg = self.CheckFFProbe(stream.url)
            self.logger.debug('[CheckTools] CheckYoutube: stream_info ' + str(stream_info) + ', msg ' + str(msg))
            if stream_info:
              stream_info = stream_info.get('streams')
            programs.append({
              'program_id': format_id,
              'url': stream.url,
              'streams': stream_info
            })
        json_data['programs'] = programs
        self.logger.debug('[CheckTools] CheckYoutube: programs ' + str(programs))
    except:
      self.logger.error('[CheckTools] YTDataToJSON: Exception error')
      raise
    return json_data


  # Check Youtube URL
  def CheckYoutube(self, url = None):
    streams = {}
    try:
      streams = streamlink.streams(url)
      self.logger.debug('[CheckTools] CheckYoutube: streams ' + str(streams))
      if streams:
        msg = 'OK'
      else:
        msg = 'No media data were found'
    except (streamlink.StreamlinkError,
            streamlink.PluginError,
            streamlink.NoPluginError,
            streamlink.StreamError) as e:
      msg = str(e)
      raise
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[CheckTools] CheckYoutube: ' + msg)
    return streams, msg


  # FFProbe checks
  def CheckFFProbe(self, media = None, timeout = 60):
    media_data = None
    # Decklink source
    decklink_pattern = [ 'DeckLink', 'Decklink', 'decklink' ]
    if any(str in media for str in decklink_pattern):
      return True, 'OK'
    # Youtube source
    youtube_pattern = [ '://www.youtube.com' ]
    if any(str in media for str in youtube_pattern):
      streams, msg = self.CheckYoutube(url = media)
      if streams:
        return self.YTDataToJSON(dict_data = streams), msg
    else:
      check_binary = app_config.FFPROBE_BIN
      check_timeout = 'timeout ' + str(timeout) + ' '
      check_format = ' -of json'
      check_duration = ' -analyzeduration 3000000' # 3 sec
      check_options = ' -hide_banner -v quiet -show_error -show_streams '
      drm_pattern = [ '.m3u8' ]
      if any(str in media for str in drm_pattern):
        check_options += ' -allowed_extensions key,ts'
      http_pattern = [ 'http://', 'https://' ]
      if any(str in media for str in http_pattern):
        protocols = ' -protocol_whitelist file,crypto,tcp,tls,http,https'
        user_agent = ' -user_agent "Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"'
        check_options += protocols + user_agent
      try:
        media_safe = ' \"' + media.replace('app/main/common/../../../','') + '\"'
        check_cmd = check_timeout + check_binary + check_format + check_duration + check_options + media_safe
        self.logger.debug('[CheckTools] CheckFFProbe: check_cmd ' + str(check_cmd))
        #stderr = open(os.devnull, 'w')
        out = check_output(shlex.split(check_cmd), close_fds = True).decode()
        #self.logger.debug('[CheckTools] CheckFFProbe: out ' + str(out))
        try:
          mi_json_data = json.loads(out)
          if any(key in list(mi_json_data.keys()) for key in [ 'programs', 'streams' ]):
            media_data = mi_json_data
            msg = 'OK'
          else:
            msg = 'No media data found'
            self.logger.error('[CheckTools] CheckFFProbe: No media data (' + str(out) + ')')
        except ValueError as e:
          msg = 'Media data error'
          self.logger.error('[CheckTools] CheckFFProbe: Media data ValueError (' + str(e) + ')')
        except:
          msg = 'Media data error (exception)'
          self.logger.error('[CheckTools] CheckFFProbe: Media data error exception')
      except CalledProcessError as e:
        try:
          output = json.loads(e.output)
          msg = output['error']['string']
        except:
          msg = 'Media check error'
          self.logger.error('[CheckTools] CheckFFProbe: CalledProcessError error (' + str(e) + ')')
      except:
        msg = 'Media check error'
        self.logger.error('[CheckTools] CheckFFProbe exception error')
    #self.logger.info('[CheckTools] CheckFFProbe: media_data ' + str(media_data))
    return media_data, msg


  # Get system info about process
  def GetProcessStats(self, sys_stats = {}, proc_info = None):
    try:
      if proc_info:
        #self.logger.debug('[CheckTools] proc_info: ' + str(proc_info))
        create_time = datetime.fromtimestamp(proc_info['create_time'])
        sys_stats['uptime'] = _SystemTools.TimeDelta(time1 = datetime.now(), time2 = create_time)
        sys_stats['cpu'] = int(proc_info['cpu_percent'] / len(proc_info['cpu_affinity']))
        sys_stats['ram'] = int(proc_info['memory_percent'])
        gpu_stats = _SystemTools.GPUStats(proc_pid = proc_info['pid'])
        #self.logger.debug('[CheckTools] gpu_stats: ' + str(gpu_stats))
        if gpu_stats and ('dev_proc' in list(gpu_stats.keys())):
          sys_stats['gpu'] = gpu_stats['dev_proc']
      else:
        self.logger.error('[CheckTools] GetProcessStats: No process found')
    except:
      self.logger.error('[CheckTools] GetProcessStats: Exception error')
      raise
    return sys_stats


  ### Check memory for FFMPEG processes ###
  def CheckMemory(self, sys_stats):
    result = False
    msg = 'ERR_ENC'
    try:
      pcmd_list = []
      pid_list = []
      self.logger.debug('[CheckTools] Memory check: Source ' + self.source)
      self.logger.debug('[CheckTools] Memory check: Target ' + self.target_first_url)
      try:
        for proc in psutil.process_iter():
          proc_info = proc.as_dict(attrs=[ 'name', 'cmdline', 'pid', 'create_time', 'cpu_percent', 'memory_percent', 'cpu_affinity' ])
          p_name = proc_info['name']
          p_cmdline = ' '.join(proc_info['cmdline'])
          p_namespace = [ 'ffmpeg', 'ffmpeg_scte35' ]
          p_pattern = [ self.target_first_url ]
#          p_pattern = [ self.source, self.target_first_url ]
          if any(p_name in ns for ns in p_namespace) and all(p in p_cmdline for p in p_pattern):
            pcmd_list.append(p_cmdline)
            pid_list.append(proc_info.get('pid'))
            sys_stats = self.GetProcessStats(sys_stats = sys_stats, proc_info = proc_info)
        proc_count = len(pid_list)
      except:
        proc_count = 1
        self.logger.debug('[CheckTools] Memory check: psutil exception error')
      if proc_count == 1:
        result = True
        msg = 'OK'
        self.logger.info('[CheckTools] Memory check: OK ' + str(pid_list))
      elif proc_count > 1:
        self.logger.error('[CheckTools] Memory check: Multiple processes detected')
        if any('nvenc' in p_cmd for p_cmd in pcmd_list):
          self.logger.warning('[CheckTools] Memory check: NVENC job detected')
#          result = True
#          msg = 'OK'
        else:
          pass
        self.logger.error('[CheckTools] Memory check: Cleaning duplicate jobs ' + str(pid_list))
        _SystemTools.PIDKill(pid_list = pid_list)
      else:
        self.logger.error('[CheckTools] Memory check: No process(es) found, restarting')
        self.EncoderStop()
        self.EncoderStart()
        self.query.uptime = None
        self.query.start_time = datetime.now()
    except:
      self.logger.error('[CheckTools] Memory check: Exception error')
    return result, msg, sys_stats


  ### Switch active source (RoundRobin) and (re)start a Job ###
  def SourceSwitch(self):
    self.logger.info('[CheckTools] Source switching init')
    self.EncoderStop()
    if self.query.source_active == 'main':
      if self.query.source_bak:
        self.query.source_active = 'backup'
      elif self.failover_use:
        self.query.source_active = 'failover'
    elif self.query.source_active == 'backup':
      if self.failover_use:
        self.query.source_active = 'failover'
      else:
        self.query.source_active = 'main'
    self.logger.info('[CheckTools] Source Switch: ' + self.query.source_active)
    self.EncoderStart()
    self.query.uptime = None
    self.query.start_time = datetime.now()


  # Copy Job logs to error folder for investigation
  def JobLogsCopy(self):
    try:
      job_logs = _FileTools.ListDir(dir = app_config.LOG_DIR_JOBS, ext = '.log', pattern = self.job_id, abs_path = True)
      for log in job_logs:
        if os.path.isfile(log):
          shutil.copy(log, app_config.LOG_DIR_ERRORS)
      self.logger.info('[CheckTools] JobLogsCopy: OK')
    except:
      self.logger.error('[CheckTools] JobLogsCopy: Exception error')
      raise


  # Check failover
  def CheckFailover(self):
    failover_on = True
    self.logger.info('[CheckTools] Failover use: ' + str(self.failover_use))
    if self.query.source_active == 'failover' and self.failover_use:
      for src in self.source_all:
        media_data, msg = self.CheckFFProbe(media = self.source_all[src], timeout = self.query.check_timeout)
        if media_data:
          self.logger.info('[CheckTools] Source recovering init')
          self.EncoderStop()
          self.logger.info('[CheckTools] Failover disabled')
          failover_on = False
          self.query.source_active = src
          self.EncoderStart()
          self.query.uptime = None
          self.query.start_time = datetime.now()
          self.logger.info('[CheckTools] Source recovered: ' + self.query.source_active)
          break
    elif self.query.source_active == 'backup' and self.query.source_main_bak_rr:
      media_data, msg = self.CheckFFProbe(media = self.source_all['main'], timeout = self.query.check_timeout)
      if media_data:
        self.logger.info('[CheckTools] Main source recovering start')
        self.EncoderStop()
        self.logger.info('[CheckTools] Backup disabled')
        failover_on = False
        self.query.source_active = 'main'
        self.EncoderStart()
        self.query.uptime = None
        self.query.start_time = datetime.now()
        self.logger.info('[CheckTools] Main source recovering complete')
      else:
        self.logger.info('[CheckTools] Main source recovering failed')
    else:
      msg = 'ERR_SRC'
    return failover_on, msg


  # Check Youtube source
  def CheckSourceYT(self):
    self.logger.debug('[CheckTools] DEBUG Youtube URL: ' + self.source)
    datetime_now = datetime.now()
    self.logger.debug('[CheckTools] Local date (UTC): ' + str(datetime_now))
    yt_expire_utc = self.source_ext['expire']
    #yt_expire_utc = 1556196016 # expired UTC
    self.logger.debug('[CheckTools] Youtube expire UTC: ' + str(yt_expire_utc))
    yt_expire_dt_local = _SystemTools.UTCtoLocal(yt_expire_utc)
    self.logger.debug('[CheckTools] Youtube expire DT local: ' + str(yt_expire_dt_local))
    if yt_expire_dt_local < datetime_now:
      yt_valid_for_dt = _SystemTools.TimeDelta(time1 = datetime_now, time2 = yt_expire_dt_local)
      self.logger.info('[CheckTools] Youtube source has expired ' + str(yt_valid_for_dt) + ' ago')
      yt_media_data, msg = self.CheckYoutube(url = self.source_all[self.query.source_active])
      if yt_media_data:
        datetime_now = datetime.now()
        self.source = yt_media_data.get(self.source_ext['format_id']).url
        self.logger.debug('[CheckTools] Youtube new source URL: ' + self.source)
        self.source_ext['url'] = self.source
        yt_expire_utc = self.YTExpireDate(url = self.source)
        self.logger.debug('[CheckTools] Youtube new expire UTC: ' + str(yt_expire_utc))
        self.source_ext['expire'] = yt_expire_utc
        yt_expire_dt_local = _SystemTools.UTCtoLocal(yt_expire_utc)
        self.logger.debug('[CheckTools] Youtube new expire DT local: ' + str(yt_expire_dt_local))
    yt_valid_for_dt = _SystemTools.TimeDelta(time1 = datetime_now, time2 = yt_expire_dt_local)
    self.logger.info('[CheckTools] Youtube source valid for: ' + str(yt_valid_for_dt))
    #self.source_ext['valid_for'] = yt_valid_for_dt


  # Check Source
  def CheckSource(self):
    if self.query.check_source:
      if self.source_youtube:
        self.CheckSourceYT()
      if any(str in self.source for str in [ 'srt://' ]) and self.SourceType()['srt_mode'] != 'caller':
        result = True
        failover_on = True
        msg = 'OK'
      else:
        failover_on, msg = self.CheckFailover()
        if failover_on:
          self.logger.info('[CheckTools] Source media: ' + self.source)
          result, msg = self.CheckFFProbe(media = self.source, timeout = self.query.check_timeout)
          if result:
            if self.query.source_active == 'failover' and self.failover_use:
              self.logger.info('[CheckTools] Failover check: ' + str(msg))
              self.logger.info('[CheckTools] Source(s) recovering failed')
              msg = 'ERR_SRC'
            else:
              self.logger.info('[CheckTools] Source check: ' + str(msg))
          else:
            self.logger.error('[CheckTools] Source check: ' + str(msg))
            self.SourceSwitch()
            msg = 'ERR_SRC'
        else:
          result = False
      return result, failover_on, msg
    else:
      self.logger.warning('[CheckTools] Source check: Disabled by user')
      return True, True, 'OK'


 ### TODO: Find a way to AUTH via ffmpeg to get DRM key ###
 ### Check first Target ###
  def CheckTarget(self):
    if self.query.check_target:
      if self.target_first_type == 'Stream':
        self.logger.info('[CheckTools] Target: ' + self.target_first_type + ' (' + self.target_first_stype + ')')
        self.logger.info('[CheckTools] Media: ' + self.target_first_url)
        if self.target_first_stype == 'HLS' and self.query.hls_drm_active and self.query.hls_drm_key_type == 'Remote':
          if self.target_first_server.ip == 'localhost':
            if os.path.isfile(self.target_first_url):
              result = True
              msg = 'OK'
            else:
              result = False
              msg = 'ERR_ENC'
          else:
            result, msg = self.CheckHTTP(url = self.target_first_url, user = self.query.hls_drm_key_user, password = self.query.hls_drm_key_password)
        elif self.target_first_stype == 'SRT':
          result = True
          msg = 'OK'
        else:
          result, msg = self.CheckFFProbe(media = self.target_first_url, timeout = self.query.check_timeout)
      if self.target_first_type == 'Device':
        self.logger.info('[CheckTools] Target: ' + self.target_first_type + ' (' + self.target_first_url + ')')
        result, msg = self.CheckFFProbe(media = self.target_first_url, timeout = self.query.check_timeout)
      if result:
        self.logger.info('[CheckTools] Target check: ' + msg)
        if self.query.source_active == 'failover' and self.failover_use:
          msg = 'ERR_SRC'
          result = False
      else:
        self.logger.error('[CheckTools] Target check: ' + msg)
        msg = 'ERR_ENC'
      return result, msg
    else:
      self.logger.warning('[CheckTools] Target check: Disabled by user')
      return True, 'OK'



  ### Stream checks: failover, memory, source, first target ###
  def CheckPostpone(self, start_time = None, timer_min = 0, timer_max = 15):
    result = False
    pp_timer = int((datetime.now() - start_time).total_seconds())
    self.logger.debug('[CheckTools] Postpone timer: ' + str(pp_timer) + ' sec')
    if (pp_timer >= timer_min) and (pp_timer <= timer_max):
      result = True
    return result, timer_max


  ### Stream checks: failover, memory, source, first target ###
  def CheckStream(self):
    if not self.query.start_time:
      self.query.start_time = datetime.now()
    sys_stats = { 'uptime': None, 'cpu': None, 'ram': None, 'gpu': None }
    result, failover_on, msg = self.CheckSource()
    if result:
      job_check_pp, pp_timer = self.CheckPostpone(start_time = self.query.start_time, timer_max = int(self.query.check_timeout/2))
      if job_check_pp:
        msg = 'UPD'
      else:
        result, msg, sys_stats = self.CheckMemory(sys_stats = sys_stats)
        self.logger.debug('[CheckTools] sys_stats: ' + str(sys_stats))
        if result:
          result, msg = self.CheckTarget()
          if result or not failover_on:
            # Job is OK, reset error counter
            self.query.uptime = copy.copy(sys_stats['uptime'])
            self.query.retries = 0
            self.logger.info('[CheckTools] Result: OK')
    if msg != 'OK':
      self.query.uptime = None
      sys_stats = { 'uptime': None, 'cpu': None, 'ram': None, 'gpu': None }
      #job_check_pp, pp_timer = self.CheckPostpone(start_time = self.query.start_time, timer_max = self.query.check_timeout)
      #if job_check_pp:
      #  msg = 'UPD'
      #  self.logger.info('[CheckTools] Result: Postponed for ' + str(pp_timer) + ' sec')
      #else:
      self.JobLogsCopy()
      self.query.retries += 1
      self.logger.info('[CheckTools] Result: Error')

    target_first_url = str(self.target_first_url)
    if self.target_first_type == 'Stream' and self.target_first_stype == 'HLS' and self.target_first_server:
      if self.target_first_server.ip == 'localhost':
        ts = target_first_url.split('/')
        target_first_url = '/'.join([ self.target_first_server.hls_srv, ts[-2], ts[-1] ])

    report_check = {
      'id': copy.copy(self.job_id),
      'source_active': copy.copy(self.query.source_active),
      'run_status': copy.copy(msg),
      'retries': copy.copy(self.query.retries),
      'start_time': copy.copy(self.query.start_time),
      'uptime': copy.copy(self.query.uptime),
      'sys_stats': copy.copy(sys_stats)
    }

    if self.source_ext and self.source_youtube:
      source_ext_db = self.SourceType()['source_ext']['key']
      report_check[source_ext_db] = copy.copy(self.source_ext)

    error_ext = { 'ERR_SRC': 'Source error', 'ERR_ENC': 'Encode error' }
    if msg in list(error_ext.keys()):
      report_error = report_check.copy()
      report_error.update({
        'sid': copy.copy(self.job_sid),
        'name': copy.copy(self.query.job_name),
        'source': copy.copy(self.SourceType()['source']),
        'target': copy.copy(target_first_url),
        'check_time': time.strftime('%x %X'),
        'msg': error_ext[msg]
      })
    else:
      report_error = None

    return report_check, report_error


  ### Run stream checks ###
  def Run(self, queue_in = None, job_id = None, report_check = [], report_error = []):
    try:
      self.logger.info('[CheckTools] ---------- Check start ----------')
      if job_id or queue_in:
        if not job_id and queue_in:
          job_id = queue_in.get()
        if job_id:
          query = Job.query.filter_by(id = job_id).first()
          self.Init(query = query, logger = self.logger)
        else:
          self.logger.warning('[CheckTools] Run: No Job ID provided')
      if self.query:
        # Run main check and collect reports
        r_update, r_error = self.CheckStream()
        report_check.append(r_update)
        if r_error:
          report_error.append(r_error)
        self.logger.info('[CheckTools] ----------- Check end -----------')
      else:
        self.logger.error('[CheckTools] Run: Init() error')
    except:
      self.logger.error('[CheckTools] Run: Exception error')
      raise
    try:
      if queue_in:
        queue_in.task_done()
    except:
      self.logger.error('[CheckTools] Run: Queue task_done() exception error')
      raise
    return report_check, report_error


  #Check reports parse
  def ReportsParse(self, report_check = [], report_error = []):
    if report_check:
      for report in report_check:
        Job.query.filter(Job.id == report.get('id'), Job.run_status != 'OFF').update(report)
    # Process error reports
    if report_error:
      _AlarmManager.OnError(report = report_error)


  ### Check stream and update Job data now ###
#  def CheckStreamNow(self, query = None):
#    self.Init(query = query)
#    self.logger.info('[CheckTools] Stream check request')
#    result = self.CheckStream()
#    Job.query.filter_by(id = query.id).update(result)
#    db_session.commit()
#    self.logger.info('[CheckTools] Check data commited to database')
#    return result

