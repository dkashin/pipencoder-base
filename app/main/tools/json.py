
from main.common.log import LogManager


# JSON tools
class JSONTools(LogManager):


  def __init__(self, logger = None):
    self.logger = logger or self.LogNull()


  # Check request with JSON
  def CheckRequest(self, request = None):
    try:
      json_data = request.get_json() or {}
      msg = 'OK'
    except:
      json_data = {}
      msg = 'Request has no JSON data'
      raise
    return json_data, msg


  # Check JSON keys
  def CheckKeys(self, json_data = {}, match_keys = []):
    result = False
    try:
      if match_keys:
        json_keys = list(json_data.keys())
        missing_json_keys = [ key for key in match_keys if not key in json_keys ]
        if missing_json_keys:
          return False, 'Required key(s): ' + str(missing_json_keys)
      msg = 'OK'
      result = True
    except:
      msg = 'JSON format error (CheckKeys)'
      raise
    return result, msg


  # Check JSON data
  def CheckIntegrity(self, request = None, json_data = {}, match_keys = []):
    result = False
    if request:
      json_data, msg = self.CheckRequest(request = request)
    if not json_data is None:
      result, msg = self.CheckKeys(json_data = json_data, match_keys = match_keys)
    else:
      msg = 'JSON format error (CheckIntegrity)'
    return result, msg, json_data


  def JSONToString(self, json_data = {}):
    try:
      string = ''
      for k in list(json_data):
        val = json_data.pop(k)
        string += '%s: %s, ' % (k, val)
    except:
      string = 'JSON to String conversion error'
      raise
    return string

