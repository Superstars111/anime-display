# Taken from https://www.askpython.com/python-modules/flask/flask-user-authentication
# and from https://realpython.com/python-sqlite-sqlalchemy/
# and from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from . import db

login = LoginManager()

friends = Table(
    "friends",
    db.metadata,
    Column("friend1_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend2_id", Integer, ForeignKey("users.id"), primary_key=True)
)

show_list = Table(
    "show_list",
    db.metadata,
    Column("list_id", Integer, ForeignKey("lists.id")),
    Column("show_id", Integer, ForeignKey("shows.id"))
)

ratings = Table(
    "ratings",
    db.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("show_id", Integer, ForeignKey("shows.id")),
    Column("score", Integer),
    Column("pacing", Integer),
    Column("drama", Integer),
    Column("realism", Integer),
    Column("propriety", Integer)
)

alt_names = Table(
    "names",
    db.metadata,
    Column("alt_name", String),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("show_id", Integer, ForeignKey("shows.id"))
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True)
    username = Column(String(100), unique=True)
    password = Column(String(100))
    admin = Column(Boolean)
    lists = relationship("List", backref=backref("users"))
    friends = relationship("User",
                           secondary=friends,
                           primaryjoin=id==friends.c.friend1_id,
                           secondaryjoin=id==friends.c.friend2_id,
                           back_populates="friends")
    # outgoing_recommendations = relationship("Recommendation", backref=backref("users"))
    # incoming_recommendations = relationship("Recommendation", backref=backref("users"))
    show_ratings = relationship("Show", secondary=ratings, back_populates="user_ratings")
    alt_show_names = relationship("Show", secondary=alt_names, back_populates="alt_names")


class Show(db.Model):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    en_name = Column(String)
    jp_name = Column(String)
    rj_name = Column(String)
    anilist_id = Column(Integer, unique=True)
    lists = relationship("List", secondary=show_list, back_populates="shows")
    recommendations = relationship("Recommendation", backref=backref("shows"))
    user_ratings = relationship("User", secondary=ratings, back_populates="show_ratings")
    alt_names = relationship("User", secondary=alt_names, back_populates="alt_show_names")


class List(db.Model):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    shows = relationship("Show", secondary=show_list, back_populates="lists")


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    show_id = Column(Integer, ForeignKey("shows.id"))

    sender = relationship("User", foreign_keys="Recommendation.sender_id")
    receiver = relationship("User", foreign_keys="Recommendation.receiver_id")
