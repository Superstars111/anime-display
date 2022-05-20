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
from project.standalone_functions import get_average
import decimal as dc

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

    def sort_shows(self) -> dict:
        sorted_shows = {
            "main_shows": [],
            "side_shows": [],
            "minor_shows": []
        }

        for show in self.shows:
            if show.priority == 1:
                sorted_shows["main_shows"].append(show)
            elif show.priority == 2:
                sorted_shows["side_shows"].append(show)
            elif show.priority == 3:
                sorted_shows["minor_shows"].append(show)

        return sorted_shows

    def average_ratings(self) -> dict:
        base_ratings = {
            "pacing": [],
            "energy": [],
            "tone": [],
            "fantasy": [],
            "abstraction": [],
            "propriety": []
        }
        for show in self.shows:
            for rating in show.user_ratings:
                    base_ratings["pacing"].append(rating.pacing)
                    base_ratings["energy"].append(rating.energy)
                    base_ratings["tone"].append(rating.tone)
                    base_ratings["fantasy"].append(rating.fantasy)
                    base_ratings["abstraction"].append(rating.abstraction)
                    base_ratings["propriety"].append(rating.propriety)

        average_ratings = {
            "pacing": get_average(base_ratings["pacing"]),
            "energy": get_average(base_ratings["energy"]),
            "tone": get_average(base_ratings["tone"]),
            "fantasy": get_average(base_ratings["fantasy"]),
            "abstraction": get_average(base_ratings["abstraction"]),
            "propriety": get_average(base_ratings["propriety"])
        }

        return average_ratings

    def ratings_by_user(self) -> list:
        user_ids = []
        show_ids = []
        all_user_series_ratings = []

        for show in self.shows:
            show_ids.append(show.id)
            for rating in show.user_ratings:
                if rating.user_id not in user_ids:
                    user_ids.append(rating.user_id)

        for user in user_ids:
            base_ratings = {
                "pacing": [],
                "energy": [],
                "tone": [],
                "fantasy": [],
                "abstraction": [],
                "propriety": []
            }

            for show in show_ids:
                rating = Rating.query.filter_by(user_id=user, show_id=show).first()
                if rating:
                    base_ratings["pacing"].append(rating.pacing)
                    base_ratings["energy"].append(rating.energy)
                    base_ratings["tone"].append(rating.tone)
                    base_ratings["fantasy"].append(rating.fantasy)
                    base_ratings["abstraction"].append(rating.abstraction)
                    base_ratings["propriety"].append(rating.propriety)

            average_ratings = {
                "pacing": get_average(base_ratings["pacing"], allow_null=True),
                "energy": get_average(base_ratings["energy"], allow_null=True),
                "tone": get_average(base_ratings["tone"], allow_null=True),
                "fantasy": get_average(base_ratings["fantasy"], allow_null=True),
                "abstraction": get_average(base_ratings["abstraction"], allow_null=True),
                "propriety": get_average(base_ratings["propriety"], allow_null=True)
            }

            all_user_series_ratings.append(average_ratings)

        return all_user_series_ratings

    def ratings_by_show(self) -> list:
        all_ratings = []
        for show in self.shows:
            all_ratings.append(show.average_ratings())

        return all_ratings


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
    status = Column(String)
    episodes = Column(Integer)
    cover_med = Column(String)
    cover_large = Column(String)
    cover_xl = Column(String)
    description = Column(String)
    series_entry_id = Column(Integer, ForeignKey("series.id"))
    series_id = Column(Integer, ForeignKey("series.id"))

    lists = relationship("List", secondary=show_list, back_populates="shows")
    recommendations = relationship("Recommendation", backref=backref("shows"))
    user_ratings = relationship("Rating", backref=backref("shows"))
    alt_names = relationship("User", secondary=alt_names, back_populates="alt_show_names")

    series_entry = relationship("Series", foreign_keys=[series_entry_id], uselist=False)
    series = relationship("Series", foreign_keys=[series_id], post_update=True)

    def average_ratings(self) -> dict:
        base_ratings = {
            "pacing": [],
            "energy": [],
            "tone": [],
            "fantasy": [],
            "abstraction": [],
            "propriety": []
        }

        for rating in self.user_ratings:
                base_ratings["pacing"].append(rating.pacing)
                base_ratings["energy"].append(rating.energy)
                base_ratings["tone"].append(rating.tone)
                base_ratings["fantasy"].append(rating.fantasy)
                base_ratings["abstraction"].append(rating.abstraction)
                base_ratings["propriety"].append(rating.propriety)

        average_ratings = {
            "pacing": get_average(base_ratings["pacing"]),
            "energy": get_average(base_ratings["energy"]),
            "tone": get_average(base_ratings["tone"]),
            "fantasy": get_average(base_ratings["fantasy"]),
            "abstraction": get_average(base_ratings["abstraction"]),
            "propriety": get_average(base_ratings["propriety"])
        }

        return average_ratings

    def update_entry(self, new_data: dict):
        self.en_name = new_data["title"]["english"]
        self.jp_name = new_data["title"]["native"]
        self.rj_name = new_data["title"]["romaji"]
        self.type = new_data["format"]
        self.status = new_data["status"]
        self.episodes = new_data["episodes"]
        self.cover_image = new_data["coverImage"]["large"]
        self.description = new_data["description"]

        # db.session.commit()


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
    tone = Column(Integer)
    fantasy = Column(Integer)
    abstraction = Column(Integer)
    propriety = Column(Integer)

    def update(self, new_data: dict):
        self.score = new_data["score"]
        self.pacing = new_data["pacing"]
        self.energy = new_data["energy"]
        self.tone = new_data["tone"]
        self.fantasy = new_data["fantasy"]
        self.abstraction = new_data["abstraction"]
        self.propriety = new_data["propriety"]
