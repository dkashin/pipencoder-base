#
#import requests, untangle
#from requests_ntlm import HttpNtlmAuth

#from xtech_live.config import BaseConfig
#

#### Manage Smooth Streaming publishing points (MS IIS) ###
#class SmoothIIS(BaseConfig):

#  def GetState(self, url = None, user = None, password = None):
#    code = 404
#    headers = { 'Content-Type': 'application/atom+xml' }
#    try:
#      r = requests.get(url + '.isml/state', headers = headers, timeout = 3, auth = HttpNtlmAuth(user, password))
#      code = r.status_code
#      if code == 200:
#        IISResponce = untangle.parse(r.text)
#        msg = IISResponce.entry.content.SmoothStreaming.State.Value.cdata
#      else:
#        msg = 'IIS GetState request error (' + str(code) + ')'
#    except RequestException as e:
#      msg = 'IIS GetState exception error (' + str(e) + ')'
#    return code, msg

#  def SetState(self, url = None, state_value = None, user = None, password = None):
#    code = 404
#    headers = { 'Content-Type': 'application/atom+xml' }
#    try:
#      xml = '<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom"><content type="application/xml"><SmoothStreaming xmlns="http://schemas.microsoft.com/iis/media/2011/03/streaming/management"><State><Value>' + state_value + '</Value></State></SmoothStreaming></content></entry>'
#      r = requests.put(url + '.isml/state', headers = headers, data = xml, timeout = 3, auth = HttpNtlmAuth(user, password))
#      code = r.status_code
#      if code == 200:
#        msg = 'IIS SetState: ' + state_value
#      else:
#        msg = 'IIS SetState request error (' + str(code) + ')'
#    except RequestException as e:
#      msg = 'IIS SetState exception error (' + str(e) + ')'
#    return code, msg

#  def Create(self, server = None, app = None, pp_name = None, user = None, password = None):
#    code = 404
#    headers = { 'Content-Type': 'application/atom+xml', 'Slug': '/' + app + '/' + pp_name + '.isml' }
#    post_url = 'http://' + server + '/services/smoothstreaming/publishingpoints.isml/settings'
#    try:
#      xml = '<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom"><content type="application/xml"><SmoothStreaming xmlns="http://schemas.microsoft.com/iis/media/2011/03/streaming/management"><Settings><Title>' + pp_name + '</Title><SourceType>Push</SourceType><AutoStart>true</AutoStart><AutoRestartOnEncoderReconnect>true</AutoRestartOnEncoderReconnect><LookAheadChunks>2</LookAheadChunks><Archive enabled="true"><Path useEventIdOnPath="false" /></Archive><ClientConnections enabled="true"><ClientManifestVersion>2.0</ClientManifestVersion></ClientConnections><ServerConnections enabled="true"><SendEndOfStreamOnStop>true</SendEndOfStreamOnStop></ServerConnections></Settings></SmoothStreaming></content></entry>'
#      r = requests.post(post_url, headers = headers, data = xml, timeout = 3, auth = HttpNtlmAuth(user, password))
#      code = r.status_code
#      if code == 200:
#        msg = 'IIS Create: OK'
#      else:
#        msg = 'IIS Create request error (' + str(code) + ')'
#    except RequestException as e:
#      msg = 'IIS Create exception error (' + str(e) + ')'
#    return code, msg

#  def Delete(self, url = None, user = None, password = None):
#    code = 404
#    headers = { 'Content-Type': 'application/atom+xml' }
#    try:
#      r = requests.delete(url + '.isml/settings', headers = headers, data = xml, timeout = 3, auth = HttpNtlmAuth(user, password))
#      code = r.status_code
#      if code == 200:
#        msg = 'IIS Delete: OK'
#      else:
#        msg = 'IIS Delete request error (' + str(code) + ')'
#    except RequestException as e:
#      msg = 'IIS Delete exception error (' + str(e) + ')'
#    return code, msg
