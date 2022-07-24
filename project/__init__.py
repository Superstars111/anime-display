# Taken from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import settings

# Potentially add to config file instead?
# "pool_pre_ping": True to set to pessimistic disconnect handling was suggested, but apparently unnecessary
db = SQLAlchemy(engine_options={"pool_recycle": 280})
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(settings)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from project.auth.auth import AUTH_BLUEPRINT as AUTH_BLUEPRINT
    app.register_blueprint(AUTH_BLUEPRINT)

    from project.general.general import GENERAL_BLUEPRINT as GENERAL_BLUEPRINT
    app.register_blueprint(GENERAL_BLUEPRINT)

    from project.community.community import COMMUNITY_BLUEPRINT as COMMUNITY_BLUEPRINT
    app.register_blueprint(COMMUNITY_BLUEPRINT)

    from project.content.content import CONTENT_BLUEPRINT as CONTENT_BLUEPRINT
    app.register_blueprint(CONTENT_BLUEPRINT)

    from project.admin.admin import ADMIN_BLUEPRINT as ADMIN_BLUEPRINT
    app.register_blueprint(ADMIN_BLUEPRINT)

    return app
