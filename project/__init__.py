# Taken from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import settings
# from .models import UserModel
# from .auth import auth as auth_blueprint
# from .main import main as main_blueprint

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(settings)
    migrate = Migrate(app, db)

    # app.config["SECRET_KEY"] = "secret-key"
    # # Not sure how this is different than app.secret_key =
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from project.auth.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from project.general.general import general as general_blueprint
    app.register_blueprint(general_blueprint)

    from project.community.community import community as community_blueprint
    app.register_blueprint(community_blueprint)

    from project.content.content import content as content_blueprint
    app.register_blueprint(content_blueprint)

    from project.admin.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app
