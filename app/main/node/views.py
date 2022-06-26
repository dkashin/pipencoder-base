
from flask import Blueprint, request, jsonify
from flask_login import login_required, fresh_login_required

from . import _NodeManager


blueprint = Blueprint('node', __name__)


# Node cloud auth
@blueprint.route('/node/auth', methods=['POST'])
@login_required
def node_auth():
  response, code, msg = _NodeManager.Service(service = 'auth', request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Node cloud activate
@blueprint.route('/node/activate', methods=['POST'])
@login_required
def node_activate():
  response, code, msg = _NodeManager.Service(service = 'activate', request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Node cloud deactivate
@blueprint.route('/node/deactivate', methods=['POST'])
@login_required
def node_deactivate():
  response, code, msg = _NodeManager.Service(service = 'deactivate', request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

