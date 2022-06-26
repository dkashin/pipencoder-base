
# Module init

from main.common.log import logger_system

from .auth import AuthManager
_AuthManager = AuthManager(logger = logger_system)

# API endpoints
from . import views
