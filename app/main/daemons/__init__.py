
# Module init

from main.common.log import logger_system
from .daemons import Daemons

_Daemons = Daemons(logger = logger_system)

from . import register
