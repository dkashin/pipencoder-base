
from flask import g
from flask.sessions import SecureCookieSessionInterface
from flask_login import user_loaded_from_header, user_loaded_from_request


class CustomSessionInterface(SecureCookieSessionInterface):

  """Disable default cookie generation."""
#  def should_set_cookie(self, *args, **kwargs):
#    return False

  """Prevent creating session from API requests."""
  def save_session(self, *args, **kwargs):
    if g.get('login_via_api'):
      return
    return super(CustomSessionInterface, self).save_session(*args, **kwargs)


@user_loaded_from_header.connect
def user_loaded_from_header(self, user = None):
  print('Login via API')
  g.login_via_api = True


@user_loaded_from_request.connect
def user_loaded_from_request(self, user = None):
  print('Login via API')
  g.login_via_api = True

