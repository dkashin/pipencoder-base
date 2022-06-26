
#  ### Smooth streaming check (IIS server) ###
#  def CheckSmooth(self, url = None, user = None, password = None):
#    result = False
#    try:
#      result, pp_state = self.GetState(url = url, user = user, password = password)
#      if pp_state == 'Started':
#        result = True
#        pp_state = 'OK'
#      else:
#        result, pp_state = self.SetState(url = url, state_value = 'Idle', user = user, password = password)
#        pp_state = 'ERR_ENC'
#    except:
#      pp_state = 'State query error (exception)'
#      raise
#    return result, pp_state



