
#from werkzeug.wsgi import DispatcherMiddleware
#from main.app import create_app as master_app
from main.app import create_app

#apps = {}
#def apps_scope():
#	try:
#		apps['/api'] = main_app()
#		print('App loaded: Main')
#	except:
#		print('App failed: Main')
		#raise
#	return apps

#apps = apps_scope()
#master_app = DispatcherMiddleware(apps.itervalues().next(), apps)
master_app = create_app()
