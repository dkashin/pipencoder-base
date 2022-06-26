
import os, time, glob

from zipfile import ZipFile, ZIP_DEFLATED

from main.common.config import app_config
from main.common.log import LogManager


# File system tools
class FileTools(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Create directory tree
  def InitDirTree(self, dir_tree = None):
    if dir_tree:
      for d in dir_tree:
        try:
          os.makedirs(d)
        except OSError as e:
          if not 'File exist' in str(e):
            self.logger.error('InitDirTree exception error: ' + str(e))
        except:
          self.logger.error('InitDirTree exception error')


  # List folder files
  def ListDir(self, dir = None, ext = None, pattern = None, abs_path = False):
    list = []
    for root, directory, file in os.walk(dir):
      for f in file:
        if abs_path:
          f = os.path.join(dir, f)
        if ext and f.endswith(ext):
          list.append(f)
        elif pattern and (pattern in f):
          list.append(f)
        else:
          list.append(f)
    return list


  # Check if file is up to date
  def HasExpired(self, file = None, expire_time = 30, remove_expired = False):
    expired = True
    try:
      if os.path.isfile(file):
        time_diff = int(time.time() - os.path.getmtime(file))
        if time_diff > expire_time:
          if remove_expired:
            os.remove(file)
        else:
          expired = False
    except:
      pass
      raise
    return expired


  def WipeFiles(self, path = None, pattern = None, time_shift = None):
    try:
      files = glob.glob(os.path.join(path, pattern))
      if files:
        for file in files:
          file_time_diff = int(time.time() - os.path.getmtime(file))
          if file_time_diff > time_shift:
            os.remove(file)
    except:
      self.logger.error('[FileTools] WipeFiles: Exception error')
      raise
    return None


  # Filesystem and app directories init
  def FSInit(self):
    try:
      dir_init = [
        app_config.MIGRATIONS_DIR,
        app_config.DRM_DIR,
        app_config.UPDATE_DIR,
        app_config.LOG_DIR_SYSTEM,
        app_config.LOG_DIR_JOBS,
        app_config.LOG_DIR_ERRORS,
        app_config.SS_DIR_SYS,
        app_config.HLS_DIR,
        app_config.IMAGES_DIR,
        app_config.CLIPS_DIR
      ]
      self.InitDirTree(dir_init)
      self.logger.info('[FileTools] FSInit: OK')
    except:
      self.logger.error('[FileTools] FSInit: Exception error')
      raise
    return None


  ### Reads file line by line, returns line array ###
  def ReadFileByLine(self, file, read_from, offset, show_lines):
    file_content = None
    if os.path.isfile(file):
      with open(file) as f:
        file_content = [ line for line in f ]
      file_length = len(file_content)
      if read_from == 'start':
        start_line = offset
        end_line = offset + show_lines
        if start_line > file_length:
          file_content = None
      else:
        start_line = max(0, file_length - offset - show_lines)
        end_line = file_length - offset
        if end_line < 0:
          file_content = None
      if file_content:
        file_content = "".join(line for line in file_content[start_line:end_line])
    else:
      file_content = 'File is not available'
    return file_content


  ### Create a ZIP archive (no compression) ###
  def CompressFiles(self, archive = None, files = None, remove = False):
    result = None
    try:
      if files:
        count = 0
        for f in files:
          if os.path.isfile(f):
            z = ZipFile(archive, 'a', compression = ZIP_DEFLATED)
            z.write(f, os.path.basename(f))
            count += 1
            if remove:
              os.remove(f)
            z.close()
        if os.path.isfile(archive) and count:
          result = archive
          msg = str(count) + ' file(s) compressed as ' + str(archive)
          self.logger.debug('[FileTools] ZIP: ' + msg)
        else:
          msg = 'No file(s) were processed'
          self.logger.warning('[FileTools] ZIP: No file(s) were processed')
      else:
        msg = 'No file(s) to compress'
        self.logger.warning('[FileTools] ZIP: No file(s) to compress')
    except:
      msg = 'Exception error'
      self.logger.error('[FileTools] ZIP: Exception error')
      raise
    return result, msg

