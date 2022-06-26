
from flask import Blueprint
from . import _Daemons


blueprint = Blueprint('daemon', __name__)


@blueprint.record_once
def register_daemons(state):
  _Daemons.CheckLoop()
  _Daemons.GarbageCollector()
  #executor = concurrent.futures.ThreadPoolExecutor(2)
  #executor.submit(_Daemons.CheckLoop(app))

