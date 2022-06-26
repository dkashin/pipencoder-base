
# Module init

from main.common.log import logger_system

from .node import NodeManager
_NodeManager = NodeManager(logger = logger_system)

# API endpoints
from . import views
