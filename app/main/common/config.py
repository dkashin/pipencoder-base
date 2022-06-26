
import os
from . import __file__

"""
Application configuration.
Most configuration is set with environment variables.
"""

class AppConfig(object):

  FLASK_ENV = os.environ.get('FLASK_ENV')
  DEBUG = FLASK_ENV == 'Development'
  DEVELOPMENT = FLASK_ENV == 'Development'
  TESTING = FLASK_ENV == 'Testing'

  SECRET_KEY = os.environ.get('SECRET_KEY')
  SESSION_PROTECTION = 'strong'
  #SESSION_REFRESH_EACH_REQUEST = True
  SESSION_COOKIE_SECURE = False # HTTPs only
  SESSION_COOKIE_HTTPONLY = True
  PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME'))
  USE_SESSION_FOR_NEXT = True
  #REMEMBER_COOKIE_DURATION = int(os.environ.get('REMEMBER_COOKIE_DURATION'))
  #REMEMBER_COOKIE_HTTPONLY = True
  #REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

  NODE_TYPE = 'Standalone'
  APP_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir)
  APPS_SCOPE_ROOT = os.path.join(APP_ROOT, os.path.pardir)
  SYSTEM_ROOT = os.path.join(APPS_SCOPE_ROOT, os.path.pardir)
  PYTHON_BIN = os.path.join(SYSTEM_ROOT, 'venv', 'bin', 'python')
  SERVICE_NAME = os.environ.get('SERVICE_NAME')
  PIP_REQ_FILE = os.path.join(SYSTEM_ROOT, 'manage', 'venv', 'requirements.txt')
  TEMPLATES_DIR = os.path.join(SYSTEM_ROOT, 'templates')
  EMAIL_TEMPLATE_ERROR = 'mail_error.html'
  EMAIL_TEMPLATE_ACTION = 'mail_action.html'

  DB_ROOT = os.path.join(SYSTEM_ROOT, 'db')
  MIGRATIONS_DIR = os.path.join(DB_ROOT, 'migrations')
  SQLALCHEMY_DATABASE_URI = os.path.join('sqlite:///' + DB_ROOT, os.environ.get('DB_NAME'))
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  LOG_DIR_ROOT = os.path.join(SYSTEM_ROOT, 'logs')
  LOG_DIR_SYSTEM = os.path.join(LOG_DIR_ROOT, 'system')
  LOG_DIR_JOBS = os.path.join(LOG_DIR_ROOT, 'jobs')
  LOG_DIR_ERRORS = os.path.join(LOG_DIR_ROOT, 'errors')
  LOG_FILE_EXT = '.log'
  LOG_SIZE_MAX = 10 * 1024 * 1024
  LOG_LEVEL_SYSTEM = 10
  LOG_LEVEL_DB = 10

  UPDATE_URL = os.environ.get('UPDATE_URL')
  UPDATE_INFO = 'update_info'
  UPDATE_FILE = 'latest_update.tar.gz'
  UPDATE_DIR = os.path.join(SYSTEM_ROOT, 'update')

  APP_BIN = os.path.join(SYSTEM_ROOT, 'bin')
  FFMPEG_BIN = os.path.join(APP_BIN, 'ffmpeg')
  FFMPEG_SCTE35_BIN = os.path.join(APP_BIN, 'ffmpeg_scte35')
  FFPROBE_BIN = os.path.join(APP_BIN, 'ffprobe')

  MEDIA_DIR = os.path.join(SYSTEM_ROOT, 'media')
  ASSETS_DIR = os.path.join(MEDIA_DIR, 'assets')
  IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
  CLIPS_DIR = os.path.join(ASSETS_DIR, 'clips')
  SS_DIR_SYS = os.path.join(MEDIA_DIR, 'ss')
  SS_DIR_WEB = '/media/ss'
  HLS_DIR = os.path.join(MEDIA_DIR, 'hls')
  HLS_MANIFEST_EXT = '.m3u8'

  PRESETS_DIR = os.path.join(SYSTEM_ROOT, 'presets')
  VPRESETS_DIR = os.path.join(PRESETS_DIR, 'video')
  APRESETS_DIR = os.path.join(PRESETS_DIR, 'audio')

  DEVICE_BRAND = [ 'decklink' ]
  DRM_DIR = os.path.join(SYSTEM_ROOT, 'drm')
  HEADERS_JSON = { 'Content-Type': 'application/json' }
  JSONIFY_PRETTYPRINT_REGULAR = True

  CLOUD_API_URL = os.environ.get('CLOUD_API_URL')
  NODE_AUTH = os.path.join(CLOUD_API_URL, 'login')
  NODE_LICENSE = os.path.join(CLOUD_API_URL, 'node', 'license')
  NODE_ACTIVATE = os.path.join(CLOUD_API_URL, 'node', 'activate')
  NODE_DEACTIVATE = os.path.join(CLOUD_API_URL, 'node', 'deactivate')


app_config = AppConfig()

