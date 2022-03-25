# Taken from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import *

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(TestingConfig())

    # app.config["SECRET_KEY"] = "secret-key"
    # # Not sure how this is different than app.secret_key =
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as primary_blueprint
    app.register_blueprint(primary_blueprint)

    return app
