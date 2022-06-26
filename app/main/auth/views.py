
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from main.common.models import User
from main.common.extensions import login_manager
from main.node import _NodeManager
from . import _AuthManager


blueprint = Blueprint('auth', __name__)


# Load account by ID
@login_manager.user_loader
def load_user(id):
  return User.get_by_id(id = id)


@login_manager.request_loader
def api_request_loader(request):
  return _AuthManager.APIKeyCheck(request = request)


# Custom auth error handler
@login_manager.unauthorized_handler
def unauthorized():
  msg = { 'msg': 'Authorize required' }
  code_msg = '401 Authorize required'
  return jsonify(msg), code_msg


# User login
@blueprint.route('/login', methods=['POST'])
def login():
  l_response, l_code, l_msg = _AuthManager.Login(request = request)
#  if l_code == 200:
#    c_response, c_code, c_msg = _NodeManager.Service(service = 'activate', request = request)
#    if c_code == 200:
#      node_data = c_response.get('node_data')
#      if node_data:
#        node_data.update({ 'status': c_msg })
#        l_response.update({ 'node_data': node_data })
  return jsonify(l_response), str(l_code) + ' ' + str(l_msg)


# Current login user
@blueprint.route('/logged_user', methods=['POST'])
@login_required
def logged_user():
  return jsonify({ 'logged_user': current_user.serialize if current_user else None }), '200 OK'


# Logout
@blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
  response, code, msg = _AuthManager.Logout(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

