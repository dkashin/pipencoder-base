
from flask_bcrypt import Bcrypt
#from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

bcrypt = Bcrypt()
#db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
