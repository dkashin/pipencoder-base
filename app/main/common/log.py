
import os, logging

from logging import Formatter, NullHandler, FileHandler
from logging.handlers import RotatingFileHandler
from .config import app_config


# Log manager class
class LogManager(object):


  def LogNull(self):
    try:
      logger = logging.getLogger()
      logger.setLevel(app_config.LOG_LEVEL_SYSTEM)
      logger.addHandler(NullHandler())
  #    logger.debug('[LOG] Logger: Null handler created')
    except:
      logger = None
      raise
    return logger


  def LogClose(self, logger = None, area = None):
    try:
      if area:
        logger = logging.getLogger(area)
      if logger.handlers:
#        logger.debug('[LOG] Logger: Handler removed (' + str(area) + ')')
        for handler in logger.handlers:
          logger.removeHandler(handler)
    except:
      pass
      raise
    return None


  def LogOpen(self, area = 'system', log_dir = app_config.LOG_DIR_SYSTEM, log_name = 'system', msg_prefix = '', size_max = 1*1024*1024):
    try:
      logger = logging.getLogger(area)
      self.LogClose(logger = logger, area = area)
      if not logger.handlers:
        logger.setLevel(app_config.LOG_LEVEL_SYSTEM)
        formatter = Formatter('%(asctime)s [%(levelname)s] ' + msg_prefix + '%(message)s', '%Y-%m-%d %H:%M:%S')
        log_file = os.path.join(app_config.LOG_DIR_ROOT, log_dir, log_name + app_config.LOG_FILE_EXT)
        handler = FileHandler(log_file, mode = 'a')
        #handler = RotatingFileHandler(log_file, mode = 'a', maxBytes = app_config.LOG_SIZE_MAX or size_max, backupCount = 2)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
#        logger.debug('[LOG] Logger: Handler created (' + str(area) + ')')
    except:
      logger = self.LogNull()
      raise
    return logger


  # Job log open
  def JobLogOpen(self, job_id = None):
    log_dir = app_config.LOG_DIR_JOBS
    log_name = str(job_id) + '_job'
    return self.LogOpen(area = log_name, log_dir = log_dir, log_name = log_name)


  # Job check log open
  def JobCheckLogOpen(self, job_id = None):
    log_dir = app_config.LOG_DIR_JOBS
    log_name = str(job_id) + '_check'
    return self.LogOpen(area = log_name, log_dir = log_dir, log_name = log_name)


# App logging init
def AppLoggerInit(app_config = None):
  logger_scope = {}
  _LogManager = LogManager()
  # Null logger
  logger_scope['null'] = _LogManager.LogNull()
  # System logger
  logger_scope['system'] = _LogManager.LogOpen()
  #logger_uwsgi = _LogManager.LogOpen(area = 'uwsgi', log_dir = 'system', log_name = 'uwsgi')
  # DB logger
  if app_config.DEBUG:
    logger_scope['db'] = _LogManager.LogOpen(area = 'sqlalchemy', log_name = 'db')
  # DB migrate sub-logger
  logger_scope['db_migrate'] = _LogManager.LogOpen(area = 'alembic', msg_prefix = '[DBMigrate] ')
  LL = { 10: 'DEBUG', 20: 'INFO' }
  logger_scope['system'].info('[SystemInit] System config: ' + app_config.FLASK_ENV)
  logger_scope['system'].info('[SystemInit] System log level: ' + LL[app_config.LOG_LEVEL_SYSTEM])
  logger_scope['system'].info('[SystemInit] Database log level: ' + LL[app_config.LOG_LEVEL_DB])
  return logger_scope


# Logger scope
logger_scope = AppLoggerInit(app_config = app_config)
logger_system = logger_scope.get('system')

