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

alt_names = Table(
    "names",
    db.metadata,
    Column("alt_name", String),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("show_id", Integer, ForeignKey("shows.id"))
)

series_relation = Table(
    "series_relation",
    db.metadata,
    Column("series1_id", Integer, ForeignKey("series.id"), primary_key=True),
    Column("series2_id", Integer, ForeignKey("series.id"), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    admin = Column(Boolean)
    lists = relationship("List", backref=backref("users"))
    friends = relationship("User",
                           secondary=friends,
                           primaryjoin=id==friends.c.friend1_id,
                           secondaryjoin=id==friends.c.friend2_id,
                           back_populates="friends")
    # outgoing_recommendations = relationship("Recommendation", backref=backref("users"))
    # incoming_recommendations = relationship("Recommendation", backref=backref("users"))
    show_ratings = relationship("Rating", backref=backref("users"))
    alt_show_names = relationship("Show", secondary=alt_names, back_populates="alt_names")


class Series(db.Model):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    en_name = Column(String)
    jp_name = Column(String)
    rj_name = Column(String)
    entry_point_id = Column(Integer, ForeignKey("shows.id"), unique=True)
    # show_ids = Column(Integer, ForeignKey("shows.id"))
    shows = relationship("Show", back_populates="series", foreign_keys="[Show.series_id]")
    entry_point = relationship("Show", foreign_keys=[entry_point_id], post_update=True)
    related_series = relationship("Series",
                                  secondary=series_relation,
                                  primaryjoin=id == series_relation.c.series1_id,
                                  secondaryjoin=id == series_relation.c.series2_id,
                                  back_populates="related_series")


class Show(db.Model):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    en_name = Column(String)
    jp_name = Column(String)
    rj_name = Column(String)
    anilist_id = Column(Integer, unique=True)
    position = Column(Integer)
    priority = Column(Integer)  # 1 = main, 2 = side, 3 = minor
    type = Column(String)
    episodes = Column(Integer)
    cover_image = Column(String)
    description = Column(String)
    series_entry_id = Column(Integer, ForeignKey("series.id"))
    series_id = Column(Integer, ForeignKey("series.id"))

    lists = relationship("List", secondary=show_list, back_populates="shows")
    recommendations = relationship("Recommendation", backref=backref("shows"))
    user_ratings = relationship("Rating", backref=backref("shows"))
    alt_names = relationship("User", secondary=alt_names, back_populates="alt_show_names")

    series_entry = relationship("Series", foreign_keys=[series_entry_id], uselist=False)
    series = relationship("Series", foreign_keys=[series_id], post_update=True)


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


class Rating(db.Model):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    show_id = Column("show_id", Integer, ForeignKey("shows.id"))
    score = Column(Integer)
    pacing = Column(Integer)
    energy = Column(Integer)
    drama = Column(Integer)
    fantasy = Column(Integer)
    abstraction = Column(Integer)
    propriety = Column(Integer)
