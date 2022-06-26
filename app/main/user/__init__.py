
# Module init

from main.common.log import logger_system

from .user import UserManager
_UserManager = UserManager(logger = logger_system)

# API endpoints
from . import views
