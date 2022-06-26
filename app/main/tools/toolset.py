
from .json import JSONTools
from .file import FileTools
from .system import SystemTools

# Complete tool set
class ToolSet(JSONTools, FileTools, SystemTools):

  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()
