
# Module init

from main.common.log import logger_system

from .pipe import MediaPipe
_MediaPipe = MediaPipe(logger = logger_system)
