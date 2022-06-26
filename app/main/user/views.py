
from flask import Blueprint, request, jsonify
from flask_login import login_required, fresh_login_required

from . import _UserManager


blueprint = Blueprint('user', __name__)


# List all users
@blueprint.route('/user/list', methods=['POST'])
@login_required
def user_list():
  response, code, msg = _UserManager.UserList(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# User add
@blueprint.route('/user/add', methods=['POST'])
@login_required
def user_add():
  response, code, msg = _UserManager.UserAdd(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# User update
@blueprint.route('/user/update', methods=['POST'])
@login_required
def user_update():
  response, code, msg = _UserManager.UserUpdate(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# User delete
@blueprint.route('/user/delete', methods=['POST'])
@login_required
def user_delete():
  response, code, msg = _UserManager.UserDelete(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

