import os


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{self.DB_SERVER}/{self.DB_NAME}"
        # DB_SERVER is defined in Production and Testing classes. Config should never be called by itself.


class ProductionConfig(Config):
    DB_SERVER = "Superstars111.mysql.pythonanywhere-services.com"
    DB_NAME = "Superstars111$anime-display"
    TESTING = False


class TestingConfig(Config):
    DB_SERVER = "localhost"
    DB_NAME = "anime_display"
    TESTING = True


settings = TestingConfig()
