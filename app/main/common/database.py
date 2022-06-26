
import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask_migrate import Migrate
from flask_migrate import migrate as MigrateScan
from flask_migrate import upgrade as MigrateUpgrade

from main.common.log import logger_scope
from main.common.config import app_config


engine = create_engine(app_config.SQLALCHEMY_DATABASE_URI, convert_unicode = True)
db_session = scoped_session(sessionmaker(autocommit = False, autoflush = False, bind = engine))
Base = declarative_base()
Base.query = db_session.query_property()


# DB migrate
def DatabaseMigrate(app):
  try:
    Migrate(app = app, db = Base, directory = app_config.MIGRATIONS_DIR, render_as_batch = app_config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:'))
    MigrateScan(directory = app_config.MIGRATIONS_DIR)
    logger_scope['db_migrate'].info('Init OK')
    try:
      MigrateUpgrade(directory = app_config.MIGRATIONS_DIR)
      logger_scope['db_migrate'].info('Upgrade OK')
    except:
      logger_scope['db_migrate'].error('Upgrade failed')
      raise
  except:
    logger_scope['db_migrate'].error('Scan failed')
    raise
  return None


# Set DB default values
def DatabaseDefaults():
  from main.common.models import User, Settings, Server
  try:
    db_exist = User.query.first()
    if not db_exist:
      super_user = User(
      **{
        'username': 'power',
        'password': '$Qh8Kv#1Za',
        'admin': True
        })
      super_user.su = True
      default_user = User(
      **{
        'username': 'admin',
        'password': 'admin',
        'admin': True
        })
      default_settings = Settings(
      **{
        'default_fail_type': 'Clip',
        'default_fail_src': '01_please_stand_by_480.ts',
        'default_fail_vpid': '#256',
        'default_fail_loop': True,
        'default_fail_decoder': 'libavcodec',
        'default_fail_decoder_err_detect': 'crccheck',
        'smtp_host': 'localhost',
        'smtp_port': 25,
        'smtp_user': 'report@yourmailserver.com',
        'alarm_error_period': 60,
        'alarm_error_value': 60,
        'alarm_action_count': 10,
        'alarm_master_subject': 'Report',
        'alarm_error_subject': 'Error Report',
        'alarm_action_subject': 'Action Report',
        'version': '2.4.6'
        })
      default_server = Server(
      **{
        'name': 'This server',
        'ip': 'localhost',
        'hls_srv': 'http://localhost/media/hls'
        })
      default_server_webdav = Server(
      **{
        'name': 'WebDAV Local',
        'ip': '127.0.0.1',
        'hls_srv': 'http://127.0.0.1/hls'
        })
      db_session.add_all([
        super_user, default_user, default_settings, default_server, default_server_webdav
      ])
#      User.query.filter_by(username = 'power').update({ 'su': True })
      db_session.commit()
      logger_scope['system'].info('[Database] Defaults applied')
  except:
    logger_scope['system'].error('[Database] Defaults error')
    raise
  return None


# DB init
def db_init(app):

  with app.app_context():
    import main.common.models
    Base.metadata.create_all(bind = engine)
    DatabaseMigrate(app)
    DatabaseDefaults()

  # Remove scoped session on app shutdown
  @app.teardown_appcontext
  def shutdown_session(exception = None):
    db_session.remove()

  return None


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
#  cursor.execute("PRAGMA foreign_keys = ON")
  cursor.execute("PRAGMA page_size = 4096")
  cursor.execute("PRAGMA cache_size = 20000")
  cursor.execute("PRAGMA temp_store = MEMORY")
  cursor.execute("PRAGMA synchronous = NORMAL")
  cursor.execute("PRAGMA journal_mode = WAL")
  cursor.close()

