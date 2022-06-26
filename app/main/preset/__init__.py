
# Module init

from main.common.log import logger_system

from .preset import PresetsManager
_PresetsManager = PresetsManager(logger = logger_system)

# API endpoints
from . import views
