import os


class Config(object):
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_SERVER = "localhost"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{self.DB_SERVER}/anime_display"


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True


settings = TestingConfig()
