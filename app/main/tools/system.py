
import os, smtplib, signal, time, psutil, binascii, shlex, threading, re, random, socket, uuid, tarfile, requests

from pynvml import *
#from pynvml import _nvmlGetFunctionPointer, _nvmlCheckReturn
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPException
from socket import error as socket_error
from email.mime.multipart import MIMEMultipart as EmailMIMEMultipart
from email.mime.text import MIMEText as EmailMIMEText
from email.mime.base import MIMEBase as EmailMIMEBase
from email import encoders as EmailEncoders
from subprocess import Popen, STDOUT, check_output, CalledProcessError
from datetime import datetime
from requests.exceptions import RequestException
from tarfile import TarError

from . import _JSONTools, _FileTools
from main.common.config import app_config
from main.common.log import LogManager
from main.common.models import Job, Settings
from main.common.database import db_session
from main.common.extensions import bcrypt
from main.common.wrappers import threaded


# System tools
class SystemTools(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  def WANCheck(self, host = "8.8.8.8", port = 53, timeout = 3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    if app_config.FLASK_ENV == 'Development':
      result = True
      msg = 'WAN check disabled (dev)'
    else:
      result = False
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        result = True
        msg = 'Host is WAN connected'
        self.logger.debug('[SystemTools] Host is WAN connected')
      except Exception as e:
        if e:
          msg_e = ' (' + str(e) + ')'
        else:
          msg_e = ''
        msg = 'No internet connection'
        self.logger.error('[SystemTools] Host has no internet connection' + msg_e)
      except:
        msg = 'Exception error (WANCheck)'
        raise
    return result, msg


  # Network info
  def NetworkInfoGet(self):
    interfaces = []
    try:
      for iface, snics in list(psutil.net_if_addrs().items()):
        iface_base = re.split(':', iface)[0]
        if iface != 'lo':
          iface_exists = -1
          interface = { 'iface': iface_base, 'ip': [] }
          if interfaces:
            for idx, item in enumerate(interfaces):
              if item['iface'] == iface_base:
                interface = item
                iface_exists = idx
                break
          for snic in snics:
            if snic.family == psutil.AF_LINK:
              interface['mac'] = snic.address
            if snic.family == socket.AF_INET and snic.address != '127.0.0.1':
              interface['ip'].append(snic.address)
          if iface_exists >= 0:
            interfaces[iface_exists] = interface
          else:
            if interface['ip']:
              interfaces.append(interface)
    except:
      self.logger.error('[SystemTools] Interfaces info exception error')
      raise
    return interfaces


  # Complete host info
  def HostDataGet(self):
    hostdata = { 'hostname': None, 'uuid': None, 'interfaces': [] }
    hostdata.update({ 'uuid': self.UUIDGet() })
    # Get host name
    try:
      hostdata.update({ 'hostname': socket.gethostname() })
    except:
      self.logger.error('[SystemTools] Host name get error')
      raise
    hostdata.update({ 'interfaces': self.NetworkInfoGet() })
    self.logger.debug('[SystemTools] Host data: ' + str(hostdata))
    return hostdata


  def UUIDMix(self, node_uuid = None):
    uuid_mix = None
    try:
      node_uuid = re.split('-', node_uuid)
      uuid_new = str(uuid.uuid4()).upper()
      uuid_new = re.split('-', uuid_new)
      mix_ids = random.sample(list(range(0, len(uuid_new) - 1)), 2)
      uuid_mix = [ node_uuid[i] if (i in mix_ids) else v for (i, v) in enumerate(uuid_new) ]
      uuid_mix_join = ''
      for (i, v) in enumerate(uuid_mix):
        if i == 0:
          uuid_mix_join += v + str(mix_ids[0])
        elif i == (len(uuid_mix) - 1):
          uuid_mix_join += str(mix_ids[1]) + v
        else:
          uuid_mix_join += v
        if i < (len(uuid_mix) - 1):
          uuid_mix_join += '-'
      uuid_mix = uuid_mix_join
      #self.logger.debug('[SystemTools] Mix UUID: ' + str(uuid_mix))
    except:
      self.logger.error('[SystemTools] Mix UUID exception error')
      raise
    return uuid_mix


  # Unique Unix OS ID
  def UUIDGet(self):
    node_uuid = None
    try:
      uuid_case = [ 'sudo cat /sys/class/dmi/id/product_uuid', 'sudo dmidecode -s system-uuid']
      for uu in uuid_case:
        node_uuid = (check_output(shlex.split(uu), close_fds = True).rstrip()).decode()
        uuid_valid = re.findall('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', node_uuid, re.IGNORECASE)
        if uuid_valid:
          #node_uuid = self.UUIDMix(node_uuid = node_uuid)
          self.logger.debug('[SystemTools] UUIDGet: OS UUID ' + node_uuid)
          return node_uuid
        else:
          msg = 'Invalid UUID value'
    except CalledProcessError as e:
      msg = 'Exception error (' + str(e) + ')'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] UUIDGet: ' + msg)
    return node_uuid


  def UUIDDecode(self, node_uuid = None, node_hashkey = None):
    result = False
    try:
      node_uuid_split = re.split('-', node_uuid)
      unique_node_id = node_uuid_split[0] + node_uuid_split[len(node_uuid_split) - 1]
      self.logger.debug('[SystemTools] Node unique ID: ' + str(unique_node_id))
      self.logger.debug('[SystemTools] Key decode: node_hashkey ' + str(node_hashkey))
      self.logger.debug('[SystemTools] Key decode: unique_node_id ' + str(unique_node_id))
#      node_hash = bcrypt.generate_password_hash(unique_node_id)
#      self.logger.debug('[SystemTools] Key decode: unique_node_id local encode ' + str(node_hash))
      if node_hashkey:
        try:
          result = bcrypt.check_password_hash(node_hashkey, unique_node_id)
          msg = 'OK'
        except:
          msg = 'Invalid key'
          raise
      self.logger.debug('[SystemTools] Key decode: ' + msg)
    except:
      msg = 'Key decode exception error'
      self.logger.error('[SystemTools] Key decode: Exception error')
      raise
    return result, msg


  ### Kills selected process(es) by PID ###
  def PIDKill(self, pid_list = None):
    try:
      for pid in pid_list:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
      msg = 'OK ' + str(pid_list)
      self.logger.debug('[SystemTools] PIDKill: ' + msg)
      return True
    except OSError as e:
      msg = 'Exception error (' + str(e) + ')'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] PIDKill: ' + msg)
    return False, msg


  # Random binary/hex generator
  def DRMKeygen(self, request = None, json_data = None):
    response = {}
    try:
      key_binary = os.urandom(16)
      key_hex = binascii.hexlify(key_binary).decode()
      self.logger.debug('[SystemTools] New hex key: ' + key_hex)
      response.update({ 'key': key_hex })
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] DRMKeygen: ' + msg)
    return response, 400, msg


  # Send email to user/list
  def SendEmail(self, host = None, port = None, user = None, password = None, SSL = False, TLS = False, subject = None, mail_to = None, template = None, report = None, file_attach = None, delete_attach = False):
    result = False
    try:
      msg = EmailMIMEMultipart()
      msg['From'] = user
      msg['To'] = mail_to
      msg['Subject'] = subject
      if file_attach and os.path.isfile(file_attach):
        attachment = open(file_attach, 'rb')
        part = EmailMIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        EmailEncoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=' + file_attach)
        msg.attach(part)
      if template:
        msg.attach(EmailMIMEText(template, 'html'))
      else:
        msg.attach(EmailMIMEText(report, 'plain'))
      if SSL:
      ## Connect to SSL host
        mailserver = SMTP_SSL(host, port, host, 10)
      else:
      ## Connect to regular host
        mailserver = SMTP(host, port, host, 10)
      # identify ourselves to smtp client
      mailserver.ehlo()
      # secure our email with TLS encryption
      if TLS or ('gmail' in host):
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
      if user and password:
        mailserver.login(user, password)
      # Mail sending
      mailserver.sendmail(user, mail_to.split(','), msg.as_string())
      mailserver.quit()
      result = True
      self.logger.debug('[SystemTools] Email: Sent to (' + str(mail_to) + ')')
    except (SMTPException, SMTPAuthenticationError, smtplib.socket.gaierror, socket_error) as e:
      self.logger.error('[SystemTools] Email: Send error (' + str(e) + ')')
    except:
      self.logger.error('[SystemTools] Email: Exception error')
      raise
    if file_attach and delete_attach:
      if os.path.isfile(file_attach):
        os.remove(file_attach)
    return result


  # External app settings
  def SubProcessSetup(self):
    os.setpgrp()
    # Ignore the SIGINT signal by setting the handler to the standard signal handler SIG_IGN
    #signal.signal(signal.SIGQUIT, signal.SIG_IGN)


  # Restart service
#  @threaded
  def AppRestart(self, request = None, json_data = None, service_name = ''):
    response = {}
    try:
      cmd = shlex.split('sudo systemctl restart ' + str(service_name))
      t = threading.Thread(target = Popen, args = [ cmd ])
      t.daemon = True
      t.start()
      self.logger.info('[SystemTools] AppRestart: OK')
      return response, 200, 'OK'
    except CalledProcessError as e:
      msg = 'System error (' + str(e) + ')'
      raise
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] AppRestart: ' + msg)
    return response, 400, msg


  # Reboot server
  def SystemReboot(self, request = None, json_data = None):
    from . import _AlarmManager
    response = {}
    try:
      _AlarmManager.OnAction(report = { 'event': 'Server reboot', 'info': 'OK' })
      cmd = shlex.split('sudo reboot')
      t = threading.Timer(1, Popen, args = [ cmd ])
      t.daemon = True
      t.start()
      self.logger.info('[SystemTools] SystemReboot: OK')
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] SystemReboot: ' + msg)
    return response, 400, msg


  ### Get all GPU info and statistics
  def GPUStats(self, proc_pid = None):

#    def nvmlSystemGetCudaDriverVersion():
#      c_version = c_int()
#      fn = _nvmlGetFunctionPointer("nvmlSystemGetCudaDriverVersion")
#      ret = fn(byref(c_version))
#      _nvmlCheckReturn(ret)
#      ver_str = str(c_version.value)
#      version_str = ver_str[:2] + '.' + ver_str[-2:-1]
#      return version_str

    gpu_stats = { 'msg': 'Idle' }
    try:
      nvmlInit()
      device_count = nvmlDeviceGetCount()
      if device_count:
        try:
          gpu_stats['driver_ver'] = nvmlSystemGetDriverVersion()
#          gpu_stats['cuda_ver'] = nvmlSystemGetCudaDriverVersion()
        except NVMLError as e:
          gpu_stats['msg'] = 'GPU driver data error' + str(e) + ')'
        except:
          gpu_stats['msg'] = 'GPU driver data error'
        gpu_stats['dev_count'] = device_count
        gpu_stats['dev_data'] = []
        gpu_stats['dev_proc'] = {}
        gpu_average = 0
        gram_average = 0
        dec_util_average = 0
        enc_util_average = 0
        shift_idx = 0
        if device_count > 1:
          shift_idx = 1
        for dev_idx in range(device_count):
          dev_data_new = { 'idx': dev_idx + shift_idx, 'active': False, 'dev_name': 'GPU', 'dev_opt': { 'temp': None, 'temp_max': None, 'fan': None, 'gpu': None, 'gram': None, 'dec_util': None, 'enc_util': None }, 'msg': 'Idle' }
          handle = nvmlDeviceGetHandleByIndex(dev_idx)
          try:
            dev_data_new['dev_name'] = str(nvmlDeviceGetName(handle))
            temp = str(nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU))
            temp_max = str(nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_SLOWDOWN))
            fan = nvmlDeviceGetFanSpeed(handle)
            gpu = int(nvmlDeviceGetUtilizationRates(handle).gpu)
            gpu_average += gpu
            gram_total = float(nvmlDeviceGetMemoryInfo(handle).total)
            gram_used = float(nvmlDeviceGetMemoryInfo(handle).used)
            gram = int((gram_used / gram_total) * 100)
            gram_average += gram
            dec_util, ssize = nvmlDeviceGetDecoderUtilization(handle)
            dec_util_average += dec_util
            enc_util, ssize = nvmlDeviceGetEncoderUtilization(handle)
            enc_util_average += enc_util
#            enc_h264 = nvmlDeviceGetEncoderCapacity(handle, NVML_ENCODER_QUERY_H264)
#            enc_hevc = nvmlDeviceGetEncoderCapacity(handle, NVML_ENCODER_QUERY_HEVC)
            dev_data_new['dev_opt'] = { 'temp': temp, 'temp_max': temp_max, 'fan': fan, 'gpu': gpu, 'gram': gram, 'dec_util': dec_util, 'enc_util': enc_util }
            if gpu or gram:
              dev_data_new['active'] = True
            if proc_pid:
              # Encoder process info
              try:
                p_list = nvmlDeviceGetComputeRunningProcesses(handle)
                for p in p_list:
                  if p.pid == proc_pid:
                    gpu_stats['dev_proc'] = {
                      'idx': dev_idx,
                      'gram': int(p.usedGpuMemory / 1024 / 1024)
                    }
              except NVMLError as e:
                gpu_stats['dev_proc'] = { 'msg': 'GPU job data error (' + str(e) + ')' }
              except:
                gpu_stats['dev_proc'] = { 'msg': 'GPU job data error' }
          except NVMLError as e:
            dev_data_new['msg'] = 'GPU device data error (' + str(e) + ')'
          except:
            dev_data_new['msg'] = 'GPU device data error'
          gpu_stats['dev_data'].append(dev_data_new)
        if device_count > 1:
          gpu_average = gpu_average / device_count
          gram_average = gram_average / device_count
          dec_util_average = dec_util_average / device_count
          enc_util_average = enc_util_average / device_count
          stat_average = { 'idx': 0, 'active': True, 'dev_name': 'GPU Average', 'dev_opt': { 'gpu': gpu_average, 'gram': gram_average, 'dec_util': dec_util_average, 'enc_util': enc_util_average }, 'msg': 'Idle' }
          gpu_stats['dev_data'].insert(0, stat_average)
    except:
      gpu_stats['msg'] = 'GPU is not detected'
    return gpu_stats


  ### Get CPU/RAM info and statistics
  def HardwareStats(self):
    hard_stats = {}
    try:
      hard_stats['cpu'] = int(psutil.cpu_percent(interval = None))
      hard_stats['ram'] = int(psutil.virtual_memory().percent)
      hard_stats['gpu'] = self.GPUStats()
    except:
      self.logger.error('[SystemTools] Hardware stats: Exception error')
    return hard_stats


  ### Get jobs statistics
  def JobStats(self):
    job_stats = { 'all': 0, 'ok': 0, 'err_src': 0, 'err_enc': 0, 'off': 0, 'upd': 0 }
    try:
      query = Job.query.all()
      for q in query:
        job_stats['all'] += 1
        if (q.run_status == "OFF"): job_stats['off'] += 1
        if (q.run_status == "OK"): job_stats['ok'] += 1
        if q.run_status == "ERR_SRC": job_stats['err_src'] += 1
        if q.run_status == "ERR_ENC": job_stats['err_enc'] += 1
        if q.run_status == "UPD": job_stats['upd'] += 1
      job_stats['active'] = job_stats['all'] - job_stats['off']
    except:
      self.logger.error('[SystemTools] Jobs stats: Exception error')
      raise
    return job_stats


  def SystemStats(self, request = None, json_data = None):
    response = {}
    try:
      response_data = {
        'jobs': self.JobStats(),
        'hardware': self.HardwareStats()
      }
      response.update(response_data)
      return response, 200, 'OK'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] SystemStats: ' + msg)
    return response, 400, msg


  def UTCtoLocal(self, utc):
    try:
      utc = datetime.utcfromtimestamp(float(utc))
      epoch = time.mktime(utc.timetuple())
      offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
      return utc + offset
    except:
      return utc


  ### Time delta ###
  def TimeDelta(self, time1 = None, time2 = None):
    delta = abs(time1 - time2)
    if delta.days:
      days = str(delta.days) + 'd '
    else:
      days = ''
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = str(hours).zfill(2)
    minutes = str(minutes).zfill(2)
    seconds = str(seconds).zfill(2)
    delta = days + hours + ':' + minutes + ':' + seconds
    return delta


  # Get system log file(s) content
  def GetLog(self, request = None, json_data = None):
    response = {}
    try:
      json_check, msg, json_data = _JSONTools.CheckIntegrity(request = request, json_data = json_data, match_keys = [ 'log_dir', 'log_name', 'read_from', 'offset', 'show_lines' ])
      if json_check:
        log_dir = os.path.join(app_config.LOG_DIR_ROOT, json_data.get('log_dir'))
        log_name = json_data.get('log_name')
        log_file = os.path.join(log_dir, log_name)
        content = _FileTools.ReadFileByLine(log_file, json_data.get('read_from'), json_data.get('offset'), json_data.get('show_lines'))
        response.update({ 'content': str(content) or None })
        return response, 200, 'OK'
    except:
      msg = 'Exception error'
#      raise
    self.logger.error('[SystemTools] GetLog: ' + msg)
    return response, 400, msg


  # Check and install Python/PIP requirements
  def PipInit(self):
    try:
      pip_result = []
      pip_update = [ app_config.PYTHON_BIN, '-m', 'pip', 'install', '--no-input', '--no-cache-dir', '--disable-pip-version-check', '-r', app_config.PIP_REQ_FILE ]
      pip_result = check_output(pip_update, close_fds = True).decode()
      pip_result = pip_result.splitlines()
#      self.logger.info('[SystemTools] PipInit: CMD output ' + str(pip_result))
      if pip_result:
        pip_msg_exclude = [ 'DEPRECATION', 'Requirement already satisfied' ]
        for pip in pip_result:
          if not any(pip_msg in pip for pip_msg in pip_msg_exclude):
            self.logger.info('[SystemTools] PipInit: ' + str(pip))
        self.logger.info('[SystemTools] PipInit: OK')
    except CalledProcessError as e:
      self.logger.error('[SystemTools] PipInit: Exception error (' + str(e) + ')')
    except ValueError as e:
      self.logger.error('[SystemTools] PipInit: Exception error (' + str(e) + ')')
    except:
      self.logger.error('[SystemTools] PipInit: Exception error')
      raise
    return None


  def UpdateCheck(self, request = None, json_data = None):
    response = {}
    code = 400
    try:
      query = Settings.query.first()
      current_version = query.version
      response.update({ 'current_version': current_version })
      update_url = os.path.join(app_config.UPDATE_URL, app_config.UPDATE_INFO)
#      self.logger.debug('[SystemTools] UpdateCheck: update_url ' + update_url)
      r = requests.get(update_url, headers = app_config.HEADERS_JSON, timeout = 3)
      code = r.status_code
      if code == 200:
        try:
          update_info = r.json()
          response.update(update_info)
          json_check, msg, json_data = _JSONTools.CheckIntegrity(json_data = update_info, match_keys = [ 'new_version' ])
          if json_check:
            new_version = update_info.get('new_version')
            new_version = list(map(int, new_version.split('.')))
            current_version = list(map(int, current_version.split('.')))
            if new_version > current_version:
              response.update({ 'update_required': True })
          return response, 200, 'OK'
        except:
          msg = 'JSON format error'
          code = 400
          #raise
      else:
        msg = 'URL request error (HTTP ' + str(code) + ')'
    except RequestException as e:
      msg = 'URL request exception error (' + str(e) + ')'
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] UpdateCheck: ' + msg)
    return response, code, msg


  def UpdateGet(self):
    try:
      remote_update_file = os.path.join(app_config.UPDATE_URL, app_config.UPDATE_FILE)
      file = requests.get(remote_update_file, timeout = 3, stream = True)
      if file.status_code >= 200 and file.status_code < 300:
        local_update_file = os.path.join(app_config.UPDATE_DIR, app_config.UPDATE_FILE)
        with open(local_update_file, 'wb') as fd:
          for chunk in file.iter_content(chunk_size = 1024):
            if chunk:
              fd.write(chunk)
        self.logger.debug('[SystemTools] UpdateGet: Content file downloaded ' + str(app_config.UPDATE_FILE))
        return
      else:
        msg = 'Update file is not found'
    except RequestException as e:
      msg = 'Update file download error (' + str(e) + ')'
      raise
    except:
      msg = 'Update file exception error'
      raise
    self.logger.error('[SystemTools] UpdateGet: ' + str(msg))
    return


  @threaded
  def UpdateExtract(self):
    try:
      local_update_file = os.path.join(app_config.UPDATE_DIR, app_config.UPDATE_FILE)
      tar = tarfile.open(local_update_file)
      tar.extractall(path = app_config.SYSTEM_ROOT)
      tar.close()
      self.logger.debug('[SystemTools] UpdateExtract: Content extracted')
      os.remove(local_update_file)
      self.AppRestart(service_name = app_config.SERVICE_NAME)
      return
    except (TarError, IOError) as e:
      msg = 'Update file extract error (' + str(e) + ')'
      raise
    except:
      msg = 'Update file extract exception error'
      raise
    self.logger.error('[SystemTools] UpdateExtract: ' + str(msg))
    return


  def UpdateApply(self, request = None, json_data = None):
    from . import _AlarmManager
    response = {}
    try:
      response_upd, code, msg = self.UpdateCheck()
      if code == 200:
        new_version = response_upd.get('new_version')
        if response_upd.get('update_required'):
          response.update({ 'new_version': new_version })
          self.UpdateGet()
          Settings.query.update({ 'version': new_version })
          db_session.commit()
          self.logger.info('[SystemTools] UpdateApply: New version is ' + new_version)
          report = { 'event': 'System update', 'info': 'New version: ' + new_version }
          _AlarmManager.OnAction(report = report)
          self.UpdateExtract()
        else:
          msg = f'System is up to date [{new_version}]'
          self.logger.info(f'[SystemTools] UpdateApply: System is up to date [{new_version}]')
        return response, code, msg
    except:
      msg = 'Exception error'
      raise
    self.logger.error('[SystemTools] UpdateApply: ' + msg)
    return response, 400, msg

