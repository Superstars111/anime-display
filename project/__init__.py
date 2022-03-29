# Taken from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import settings
# from .models import UserModel
# from .auth import auth as auth_blueprint
# from .main import main as main_blueprint

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(settings)

    # app.config["SECRET_KEY"] = "secret-key"
    # # Not sure how this is different than app.secret_key =
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import UserModel

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
