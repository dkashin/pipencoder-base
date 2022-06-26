
# Module init

from main.common.log import logger_system

from .media import MediaManager
_MediaManager = MediaManager(logger = logger_system)

# API endpoints
from . import views
