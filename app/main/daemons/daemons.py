
import time, threading, queue
from datetime import datetime, timedelta

from main.common.config import app_config
from main.common.wrappers import threaded
from main.common.database import db_session
from main.common.models import Job
from main.check.check import CheckTools
from main.common.log import LogManager
from main.tools import _FileTools


# System services and daemons
class Daemons(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Jobs loop check
  @threaded
  def CheckLoop(self):
    queue_exist = True
    while True:
      try:
        time.sleep(10)
        query = Job.query.filter(Job.run_status != 'OFF').order_by(Job.id.asc()).all()
        if query:
          queue_in = queue.Queue()
          report_check = []
          report_error = []
          for q in query:
            q_id = str(q.id)
            # TODO: check if class instange needs to be wiped
            _CheckTools = CheckTools(logger = self.JobCheckLogOpen(job_id = q_id))
            check_setup = {
              'queue_in': queue_in,
              'report_check': report_check,
              'report_error': report_error
            }
            t = threading.Thread(target = _CheckTools.Run, kwargs = check_setup)
            t.daemon = True
            t.start()
            #_JobsPool.append({ 'id': q_id, 'thread': t })
            queue_in.put(q_id)
            queue_exist = True
          queue_in.join()
          _CheckTools.ReportsParse(report_check = report_check, report_error = report_error)
          db_session.commit()
        elif queue_exist:
          queue_exist = False
          self.logger.info('[Daemons] CheckLoop: Queue is empty')
        self.logger.info('[Daemons] CheckLoop: Heartbeat OK')
      except:
        db_session.rollback()
        self.logger.error('[Daemons] CheckLoop: Exception error')
        self.logger.error('[Daemons] CheckLoop: Heartbeat FAIL')
        raise


  @threaded
  def GarbageCollector(self):
    """Clean up expired screenshots, logs, media, etc"""
    while True:
      time.sleep(10)
      try:
        # Clean job log dir weekly
        _FileTools.WipeFiles(path = app_config.LOG_DIR_JOBS, pattern = '*.*', time_shift = 604800)
        # Clean system log dir daily
        _FileTools.WipeFiles(path = app_config.LOG_DIR_SYSTEM, pattern = '*.1', time_shift = 604800)
        # Clean job error log dir weekly
        _FileTools.WipeFiles(path = app_config.LOG_DIR_ERRORS, pattern = '*.*', time_shift = 604800)
        # Clean screenshots dir daily
        _FileTools.WipeFiles(path = app_config.SS_DIR_SYS, pattern = '*.jpg', time_shift = 86400)
        self.logger.info('[Daemons] GarbageCollector: OK')
      except:
        self.logger.error('[Daemons] GarbageCollector: Exception error')
        raise


