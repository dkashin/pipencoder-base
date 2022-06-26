
from flask import Blueprint, request, jsonify
from flask_login import login_required

from . import _PresetsManager


blueprint = Blueprint('preset', __name__)


# Encoding presets list
@blueprint.route('/preset/list', methods=['POST'])
@login_required
def preset_list():
  response, code, msg = _PresetsManager.PresetsList(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Encoding presets data
@blueprint.route('/preset/data', methods=['POST'])
@login_required
def preset_data():
  response, code, msg = _PresetsManager.PresetsData(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Encoding preset add
@blueprint.route('/preset/add', methods=['POST'])
@login_required
def preset_add():
  response, code, msg = _PresetsManager.PresetAddUpdate(request = request, action = 'add')
  return jsonify(response), str(code) + ' ' + str(msg)


# Encoding preset update
@blueprint.route('/preset/update', methods=['POST'])
@login_required
def preset_update():
  response, code, msg = _PresetsManager.PresetAddUpdate(request = request, action = 'update')
  return jsonify(response), str(code) + ' ' + str(msg)


# Encoding preset delete
@blueprint.route('/preset/delete', methods=['POST'])
@login_required
def preset_delete():
  response, code, msg = _PresetsManager.PresetDelete(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

