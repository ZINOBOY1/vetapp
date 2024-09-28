from flask import Flask
import os
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
from vetapp.models import db

load_dotenv()



API_KEY = os.getenv('MY_API_KEY')




csrf= CSRFProtect()




def create_app():
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py',silent=True)

    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)
    
    return app

app = create_app()

# app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
from vetapp import route_user,admin_routes
