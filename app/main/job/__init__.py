
# Module init

from main.common.log import logger_system

from .job import JobManager
_JobManager = JobManager(logger = logger_system)

# API endpoints
from . import views
