
import os, time, socket, requests, threading

from requests.exceptions import RequestException
from flask import current_app, render_template
from flask_login import current_user

from main.common.config import app_config
from main.common.models import Settings
from main.common.log import LogManager
from . import _FileTools, _SystemTools


### System alarms generator ###
class AlarmManager(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()
    self.alarm_timer = time.time()
    self.action_report = []
    self.action_counter = 0


  # Get alarm settings
  def LoadSettings(self):
    self.set_query = Settings.query.first()
    self.mail_to = self.set_query.alarm_master_email
    self.subject = self.set_query.alarm_master_subject
    return None


  # Sent alarm email
  def ProcessEmail(self, report = {}, template = None):
#    self.logger.debug(f'[ProcessEmail] report: {report}')
    info = { 'host': socket.gethostname(), 'report': report }
    try:
      with current_app.app_context():
        template = render_template(template, info = info)
      email_setup = { 'host': self.set_query.smtp_host, 'port': self.set_query.smtp_port, 'user': self.set_query.smtp_user, 'password': self.set_query.smtp_pass, 'SSL': self.set_query.smtp_ssl, 'TLS': self.set_query.smtp_tls, 'subject': self.subject, 'mail_to': self.mail_to, 'template': template, 'report': report }
      # Send email in separate thread
      t = threading.Thread(target = _SystemTools.SendEmail, kwargs = email_setup)
      t.daemon = True
      t.start()
    except:
      self.logger.error('[AlarmManager] ProcessEmail error exception')
      raise
    return info


  # Callback run
  def ProcessCallback(self, event = None, info = None, func_type = None):
    if self.set_query.callback_url:
      info['event'] = event
      result, msg = self.Callback(url = self.set_query.callback_url, data = info)
      self.logger.info('[AlarmManager] ' + str(func_type) + ': Callback ' + str(msg))
    return None


  # Action alarms
  def OnError(self, report = None):
    try:
      self.LoadSettings()
      time_now = time.time()
      if (self.set_query.alarm_error) and (int(time_now - self.alarm_timer) >= (self.set_query.alarm_error_period * self.set_query.alarm_error_value)):
        self.logger.info('[AlarmManager] OnError: Triggered at ' + str(int(time_now - self.alarm_timer)) + ' second(s)')
        if not self.set_query.alarm_master:
          self.mail_to = self.set_query.alarm_error_email
          self.subject = self.set_query.alarm_error_subject
        info = self.ProcessEmail(report = report, template = app_config.EMAIL_TEMPLATE_ERROR)
        self.alarm_timer = time_now
        self.ProcessCallback(event = 'error', info = info, func_type = 'OnError')
    except:
      self.logger.error('[AlarmManager] OnError: Exception error')
      raise
    return None


  def OnAction(self, report = None, append = False):
    try:
      self.LoadSettings()
      if self.set_query.alarm_action:
        if not append:
          self.action_counter += 1
        report.update({
          'user': current_user.username if current_user else None,
          'time': time.strftime('%x %X')
        })
        self.action_report.append(report)
        if self.action_counter >= self.set_query.alarm_action_count:
          self.logger.info('[AlarmManager] OnAction: Triggered at ' + str(self.action_counter) + ' count(s)')
          self.action_counter = 0
          if not self.set_query.alarm_master:
            self.mail_to = self.set_query.alarm_action_email
            self.subject = self.set_query.alarm_action_subject
          info = self.ProcessEmail(report = self.action_report, template = app_config.EMAIL_TEMPLATE_ACTION)
          self.action_report = []
          self.ProcessCallback(event = 'action', info = info, func_type = 'OnAction')
    except:
      self.logger.error('[AlarmManager] OnAction: Exception error')
      raise
    return None


  ### Send callback data ###
  def Callback(self, url = None, data = None):
    result = None
    try:
      r = requests.post(url, headers = app_config.HEADERS_JSON, json = data, timeout = 3)
      code = r.status_code
      if code >= 200 and code < 400:
        msg = 'OK (' + str(code) + ')'
      else:
        msg = 'Error (' + str(code) + ')'
    except RequestException as e:
      msg = 'RequestException error (' + str(e) + ')'
    except:
      msg = 'Exception error'
      raise
    return result, msg

