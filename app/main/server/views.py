
from flask import Blueprint, request, jsonify
from flask_login import login_required

from . import _ServerManager


blueprint = Blueprint('server', __name__)


# Servers list
@blueprint.route('/server/list', methods=['POST'])
@login_required
def server_list():
  response, code, msg = _ServerManager.ServerList(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Server add
@blueprint.route('/server/add', methods=['POST'])
@login_required
def server_add():
  response, code, msg = _ServerManager.ServerAdd(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Server update
@blueprint.route('/server/update', methods=['POST'])
@login_required
def server_update():
  response, code, msg = _ServerManager.ServerUpdate(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Server delete
@blueprint.route('/server/delete', methods=['POST'])
@login_required
def server_delete():
  response, code, msg = _ServerManager.ServerDelete(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

