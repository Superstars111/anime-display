class Config(object):
    TESTING = False
    SECRET_KEY = "secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_SERVER = "localhost"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///db.sqlite"


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
