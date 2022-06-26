
# Module init

from main.common.log import logger_system


from .json import JSONTools
_JSONTools = JSONTools(logger = logger_system)

from .file import FileTools
_FileTools = FileTools()

from .system import SystemTools
_SystemTools = SystemTools(logger = logger_system)

from .alarm import AlarmManager
_AlarmManager = AlarmManager(logger = logger_system)

from .toolset import ToolSet
_ToolSet = ToolSet(logger = logger_system)

# API endpoints
from . import views
