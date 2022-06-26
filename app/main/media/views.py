
from flask import Blueprint, request, jsonify
from flask_login import login_required

from . import _MediaManager


blueprint = Blueprint('media', __name__)


# Get media file/stream info
@blueprint.route('/media/info', methods=['POST'])
@login_required
def media_info():
  response, code, msg = _MediaManager.MediaInfo(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Get local media list
@blueprint.route('/media/local', methods=['POST'])
@login_required
def media_local():
  response, code, msg = _MediaManager.MediaLocal(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

