
# Module init

from main.common.log import logger_system

from .server import ServerManager
_ServerManager = ServerManager(logger = logger_system)

# API endpoints
from . import views
