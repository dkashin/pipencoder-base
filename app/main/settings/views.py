
from flask import Blueprint, request, jsonify
from flask_login import login_required

from . import _SettingsManager


blueprint = Blueprint('settings', __name__)


# System settings load
@blueprint.route('/settings/load', methods=['POST'])
@login_required
def settings_load():
  response, code, msg = _SettingsManager.SettingsLoad(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# System settings save
@blueprint.route('/settings/save', methods=['POST'])
@login_required
def settings_save():
  response, code, msg = _SettingsManager.SettingsSave(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

