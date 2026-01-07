#packages to import and initialize

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
blacklist = set()
mail = Mail()

