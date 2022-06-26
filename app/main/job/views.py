
from flask import Blueprint, request, jsonify
from flask_login import login_required

from . import _JobManager


blueprint = Blueprint('job', __name__)


# Job list with filtering and sorting
@blueprint.route('/job/list', methods=['POST'])
@login_required
def job_list():
  response, code, msg = _JobManager.JobList(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Get job(s) status
@blueprint.route('/job/status', methods=['POST'])
@login_required
def job_status():
  response, code, msg = _JobManager.JobStatus(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Start job(s)
@blueprint.route('/job/start', methods=['POST'])
@login_required
def job_start():
  response, code, msg = _JobManager.JobStart(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Stop job(s)
@blueprint.route('/job/stop', methods=['POST'])
@login_required
def job_stop():
  response, code, msg = _JobManager.JobStop(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Restart job(s)
@blueprint.route('/job/restart', methods=['POST'])
@login_required
def job_restart():
  response, code, msg = _JobManager.JobRestart(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Add new job
@blueprint.route('/job/add', methods=['POST'])
@login_required
def job_add():
  response, code, msg = _JobManager.JobAdd(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Update a job
@blueprint.route('/job/update', methods=['POST'])
@login_required
def job_update():
  response, code, msg = _JobManager.JobUpdate(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)


# Delete a job
@blueprint.route('/job/delete', methods=['POST'])
@login_required
def job_delete():
  response, code, msg = _JobManager.JobDelete(request = request)
  return jsonify(response), str(code) + ' ' + str(msg)

