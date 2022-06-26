
from threading import Thread

def threaded(fn):

  def wrapper(*args, **kwargs):
    thread = Thread(target = fn, args = args, kwargs = kwargs)
    thread.daemon = True
    thread.start()
    return thread

  return wrapper

