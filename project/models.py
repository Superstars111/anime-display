# Taken from https://www.askpython.com/python-modules/flask/flask-user-authentication
# and from https://realpython.com/python-sqlite-sqlalchemy/
# and from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from . import db

login = LoginManager()


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))
