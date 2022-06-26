
from flask import Flask

from main.common.config import app_config
from main.common.extensions import bcrypt, login_manager
from main.common.database import db_init
from main.tools import _FileTools, _SystemTools
from main.auth.session import CustomSessionInterface

import main.auth, main.job, main.media, main.node, main.preset, main.server, main.settings, main.tools, main.user, main.daemons


def create_app():
  """Create app"""
  app = Flask(__name__, template_folder = app_config.TEMPLATES_DIR)
  app.config.from_object(app_config)
#  app.session_interface = CustomSessionInterface()
  register_extensions(app)
  register_blueprints(app)
  app_init()
  return app


def register_extensions(app):
  """Register Flask extensions"""
  bcrypt.init_app(app)
  db_init(app)
  login_manager.init_app(app)
  return None


def register_blueprints(app):
  """Register Flask blueprints"""
  url_prefix = '/api/v1'
  app.register_blueprint(main.auth.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.job.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.media.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.node.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.preset.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.server.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.settings.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.tools.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.user.views.blueprint, url_prefix = url_prefix)
  app.register_blueprint(main.daemons.register.blueprint, url_prefix = url_prefix)
  return None


def app_init():
  """Init app requirements"""
  _FileTools.FSInit()
  _SystemTools.PipInit()
  return None

