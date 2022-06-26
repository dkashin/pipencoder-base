
# Module init

from main.common.log import logger_system

from .settings import SettingsManager
_SettingsManager = SettingsManager(logger = logger_system)

# API endpoints
from . import views
