
from flask import Blueprint, request, jsonify
from flask_login import login_required

from main.common.config import app_config
from . import _SystemTools


blueprint = Blueprint('tools', __name__)


# System update check
@blueprint.route('/tools/update_check', methods=['POST'])
@login_required
def update_check():
  response, code, msg = _SystemTools.UpdateCheck(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# System update apply
@blueprint.route('/tools/update_apply', methods=['POST'])
@login_required
def update_apply():
  response, code, msg = _SystemTools.UpdateApply(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# System statistics
@blueprint.route('/tools/system_stats', methods=['POST'])
@login_required
def system_stats():
  response, code, msg = _SystemTools.SystemStats(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# App core/service restart
@blueprint.route('/tools/app_restart', methods=['POST'])
@login_required
def app_restart():
  response, code, msg = _SystemTools.AppRestart(request = request, service_name = app_config.SERVICE_NAME)
  return jsonify(response), str(code) + ' ' + str(msg)


# Reboot server
@blueprint.route('/tools/system_reboot', methods=['POST'])
@login_required
def system_reboot():
  response, code, msg = _SystemTools.SystemReboot(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# DRM keygen
@blueprint.route('/tools/drm_keygen', methods=['POST'])
@login_required
def drm_keygen():
  response, code, msg = _SystemTools.DRMKeygen(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Read system log(s)
@blueprint.route('/tools/get_log', methods=['POST'])
@login_required
def get_log():
  response, code, msg = _SystemTools.GetLog(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

