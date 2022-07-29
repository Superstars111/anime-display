# Taken from https://www.askpython.com/python-modules/flask/flask-user-authentication
# and from https://realpython.com/python-sqlite-sqlalchemy/
# and from https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

import sqlalchemy as sqa
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin, LoginManager
from . import db
from project.standalone_functions import get_average, average_ratings

login = LoginManager()

friends = sqa.Table(
    "friends",
    db.metadata,
    sqa.Column("friend1_id", sqa.Integer, sqa.ForeignKey("users.id"), primary_key=True),
    sqa.Column("friend2_id", sqa.Integer, sqa.ForeignKey("users.id"), primary_key=True)
)

show_list = sqa.Table(
    "show_list",
    db.metadata,
    sqa.Column("list_id", sqa.Integer, sqa.ForeignKey("lists.id")),
    sqa.Column("show_id", sqa.Integer, sqa.ForeignKey("shows.id"))
)

alt_names = sqa.Table(
    "names",
    db.metadata,
    sqa.Column("alt_name", sqa.String),
    sqa.Column("user_id", sqa.Integer, sqa.ForeignKey("users.id")),
    sqa.Column("show_id", sqa.Integer, sqa.ForeignKey("shows.id"))
)

series_relation = sqa.Table(
    "series_relation",
    db.metadata,
    sqa.Column("series1_id", sqa.Integer, sqa.ForeignKey("series.id"), primary_key=True),
    sqa.Column("series2_id", sqa.Integer, sqa.ForeignKey("series.id"), primary_key=True)
)


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = sqa.Column(sqa.Integer, primary_key=True)
    user_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    type = sqa.Column(sqa.Integer)  # 1 = Bug report, 2 = Feature request, 3 = Data request, 4 = Other
    status = sqa.Column(sqa.Integer)  # 1 = New feedback, 2 = Planned, 3 = In progress, 4 = Closed
    description = sqa.Column(sqa.Text)
    note = sqa.Column(sqa.Text)


class List(db.Model):
    __tablename__ = "lists"

    id = sqa.Column(sqa.Integer, primary_key=True, index=True)
    name = sqa.Column(sqa.String)
    owner_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    shows = relationship("Show", secondary=show_list, back_populates="lists")


class Rating(db.Model):
    __tablename__ = "ratings"

    id = sqa.Column(sqa.Integer, primary_key=True, index=True)
    user_id = sqa.Column("user_id", sqa.Integer, sqa.ForeignKey("users.id"))
    show_id = sqa.Column("show_id", sqa.Integer, sqa.ForeignKey("shows.id"))
    score = sqa.Column(sqa.Integer)
    pacing = sqa.Column(sqa.Integer)
    energy = sqa.Column(sqa.Integer)
    tone = sqa.Column(sqa.Integer)
    fantasy = sqa.Column(sqa.Integer)
    abstraction = sqa.Column(sqa.Integer)
    propriety = sqa.Column(sqa.Integer)

    def update(self, new_data: dict):
        """
        Updates the data associated with the Rating() object.

        Fields updated include:

        - score
        - pacing
        - energy
        - tone
        - fantasy
        - abstraction
        - propriety

        :param new_data: A dictionary with keys corresponding to a Rating() object
        """
        self.score = new_data["score"]
        self.pacing = new_data["pacing"]
        self.energy = new_data["energy"]
        self.tone = new_data["tone"]
        self.fantasy = new_data["fantasy"]
        self.abstraction = new_data["abstraction"]
        self.propriety = new_data["propriety"]

    def dictify(self) -> dict[str, int]:
        """
        Makes and returns a dictionary with the contents of the object.

        :return: A dictionary with keys and values corresponding to the Rating() object
        """
        all_rating_fields = {
            "score": self.score,
            "pacing": self.pacing,
            "energy": self.energy,
            "tone": self.tone,
            "fantasy": self.fantasy,
            "abstraction": self.abstraction,
            "propriety": self.propriety,
        }

        return all_rating_fields

    def fields(self) -> list[str]:
        """
        Returns a list of the fields contained in a Rating() object.

        :return: A list of the fields contained in a Rating() object
        """
        field_names = [
            "score",
            "pacing",
            "energy",
            "tone",
            "fantasy",
            "abstraction",
            "propriety"
        ]

        return field_names


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = sqa.Column(sqa.Integer, primary_key=True, index=True)
    sender_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    receiver_id = sqa.Column(sqa.Integer, sqa.ForeignKey("users.id"))
    show_id = sqa.Column(sqa.Integer, sqa.ForeignKey("shows.id"))

    sender = relationship("User", foreign_keys="Recommendation.sender_id")
    receiver = relationship("User", foreign_keys="Recommendation.receiver_id")


class Series(db.Model):
    __tablename__ = "series"

    id = sqa.Column(sqa.Integer, primary_key=True, index=True)
    en_name = sqa.Column(sqa.String)
    jp_name = sqa.Column(sqa.String)
    rj_name = sqa.Column(sqa.String)
    entry_point_id = sqa.Column(sqa.Integer, sqa.ForeignKey("shows.id"), unique=True)
    # show_ids = Column(Integer, ForeignKey("shows.id"))
    shows = relationship("Show", back_populates="series", foreign_keys="[Show.series_id]")
    entry_point = relationship("Show", foreign_keys=[entry_point_id], post_update=True)
    related_series = relationship("Series",
                                  secondary=series_relation,
                                  primaryjoin=id == series_relation.c.series1_id,
                                  secondaryjoin=id == series_relation.c.series2_id,
                                  back_populates="related_series")

    def sort_shows(self) -> dict[str, list[object]]:
        """
        Sorts associated shows into categories based on Show().priority.

        Dict keys are "main_shows", "side_shows", and "minor_shows".

        :return: A dictionary containing lists of Show() objects
        """
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

    def update_entry_names(self, new_data: dict[str, str]):
        """
        Updates the name fields of the series.

        Passed dict should include keys "en_name", "jp_name", and "rj_name".

        :param new_data: New names for the series
        """

        self.en_name = new_data["en_name"]
        self.jp_name = new_data["jp_name"]
        self.rj_name = new_data["rj_name"]

    def average_ratings(self, only_main: bool = False) -> dict[str, int]:
        """
        Gathers the average values of each field for all ratings across all shows in the series.

        :param only_main: If true, only collects values for shows with priority == 1
        :return: The average value for each field from a Rating() object
        """
        if only_main:
            selected_shows = self.sort_shows()["main_shows"]
        else:
            selected_shows = self.shows

        base_ratings = {}

        for show in selected_shows:
            show_ratings = show.all_ratings()
            for key, value in show_ratings.items():
                if key in base_ratings:
                    base_ratings[key].extend(value)
                else:
                    base_ratings[key] = value

        average_ratings_dict = average_ratings(base_ratings)

        return average_ratings_dict

    def ratings_from_single_user(self, user_id: int, shows_list: list[object] = None) -> dict[str, list[int]]:
        """
        Gathers every rating by a given user for the shows in the series.

        :param user_id: The ID to use for querying the database
        :param shows_list: The list of Show() objects to gather ratings on
        :return: Lists of ratings, contained by field in a dict
        """
        series_ratings = {}
        if not shows_list:
            shows_list = self.shows

        for show in shows_list:
            rating = Rating.query.filter_by(user_id=user_id, show_id=show.id).first()
            if rating:
                rating_dict = rating.dictify()
                for key, value in rating_dict.items():
                    if key in series_ratings:
                        series_ratings[key].append(value)
                    else:
                        series_ratings[key] = [value]

        return series_ratings

    def ratings_by_user(self) -> list[dict[str, int]]:
        """
        Collects each user's average ratings for the series as a whole.

        This function goes through every rating in every show in the series to find the users who have rated it. Each
        users ratings for the series are then collected and averaged. This allows graph data to be displayed on the
        series page.

        :return: All ratings for the series, grouped and averaged by user
        """
        user_ids = []
        show_ids = []
        all_user_series_ratings = []

        for show in self.shows:
            show_ids.append(show.id)
            # TODO: Going through every rating in the database for a given series likely won't scale well...
            #   Find a better solution.
            for rating in show.user_ratings:
                if rating.user_id not in user_ids:
                    user_ids.append(rating.user_id)

        for user_id in user_ids:
            all_user_ratings = self.ratings_from_single_user(user_id)

            average_ratings_dict = average_ratings(all_user_ratings)

            all_user_series_ratings.append(average_ratings_dict)

        return all_user_series_ratings

    def ratings_by_show(self) -> list[dict[str, int]]:
        """
        Collects all ratings for the series, grouped and averaged by show.

        :return: Each show's average ratings as dicts in a list
        """
        all_ratings = []
        for show in self.shows:
            all_ratings.append(show.average_ratings())

        return all_ratings


class Show(db.Model):
    __tablename__ = "shows"

    id = sqa.Column(sqa.Integer, primary_key=True)
    en_name = sqa.Column(sqa.String)
    jp_name = sqa.Column(sqa.String)
    rj_name = sqa.Column(sqa.String)
    anilist_id = sqa.Column(sqa.Integer, unique=True)
    position = sqa.Column(sqa.Integer)
    priority = sqa.Column(sqa.Integer)  # 1 = main, 2 = side, 3 = minor
    type = sqa.Column(sqa.String)
    status = sqa.Column(sqa.String)
    episodes = sqa.Column(sqa.Integer)
    cover_med = sqa.Column(sqa.Text)
    cover_large = sqa.Column(sqa.Text)
    cover_xl = sqa.Column(sqa.Text)
    description = sqa.Column(sqa.String)
    series_entry_id = sqa.Column(sqa.Integer, sqa.ForeignKey("series.id"))
    series_id = sqa.Column(sqa.Integer, sqa.ForeignKey("series.id"))

    lists = relationship("List", secondary=show_list, back_populates="shows")
    recommendations = relationship("Recommendation", backref=backref("shows"))
    user_ratings = relationship("Rating", backref=backref("shows"))
    alt_names = relationship("User", secondary=alt_names, back_populates="alt_show_names")

    series_entry = relationship("Series", foreign_keys=[series_entry_id], uselist=False)
    series = relationship("Series", foreign_keys=[series_id], post_update=True)

    def average_ratings(self) -> dict[str, int]:
        """
        Determines the average rating for the show across all users.

        :return: Average ratings for the show for each field in a Rating() object
        """
        base_ratings = self.all_ratings()

        average_ratings_dict = average_ratings(base_ratings)

        return average_ratings_dict

    def all_ratings(self) -> dict[str, list[int]]:
        """
        Collects every rating for the show.

        Every rating in the show has its values appended to lists sorted by field and put into a dictionary.

        :return: A dict with keys for each rating field, containing lists of all ratings for the show
        """
        base_ratings = {}

        if self.user_ratings:
            for rating in self.user_ratings:
                rating_dict = rating.dictify()
                for key, value in rating_dict.items():
                    if key in base_ratings.keys():
                        base_ratings[key].append(value)
                    else:
                        base_ratings[key] = [value]
        else:
            for field in Rating().fields():
                base_ratings[field] = []

        return base_ratings

    def update_entry(self, new_data: dict):
        """
        Updates the data for a show.

        Data used for the update can be recieved from an AniList API request.

        Fields updated include:

        - en_name
        - jp_name
        - rj_name
        - type
        - status
        - episodes
        - cover_med
        - cover_large
        - cover_xl
        - description

        :param new_data: Data to use for a full show update
        """
        self.en_name = new_data["title"]["english"]
        self.jp_name = new_data["title"]["native"]
        self.rj_name = new_data["title"]["romaji"]
        self.type = new_data["format"]
        self.status = new_data["status"]
        self.episodes = new_data["episodes"]
        self.cover_med = new_data["coverImage"]["medium"]
        self.cover_large = new_data["coverImage"]["large"]
        self.cover_xl = new_data["coverImage"]["extraLarge"]
        self.description = new_data["description"]

        # db.session.commit()


class Update(db.Model):
    __tablename__ = "updates"

    id = sqa.Column(sqa.Integer, primary_key=True)
    version = sqa.Column(sqa.String(100))
    type = sqa.Column(sqa.Integer)  # 1 = Bug Fix, 2 = Feature, 3 = Removal, 4 = Admin, 5 = Redesign, 6 = Code Cleanup
    comment = sqa.Column(sqa.Text)
    date = sqa.Column(sqa.Date)
    published = sqa.Column(sqa.Boolean)

    def dictify(self) -> dict:
        """
        Forms a dictionary with the contents of the object. Text is substituted for ints in self.type.

        :return: A dictionary of the Update() object
        """

        if self.type == 1:
            type_text = "Bug Fix"
        elif self.type == 2:
            type_text = "Feature"
        elif self.type == 3:
            type_text = "Removal"
        elif self.type == 4:
            type_text = "Admin"
        elif self.type == 5:
            type_text = "Redesign"
        else:  # self.type == 6
            type_text = "Code Cleanup"

        update_dict = {
            "version": self.version,
            "type": type_text,
            "comment": self.comment,
            "date": self.date,
            "published": self.published
        }

        return update_dict


class User(UserMixin, db.Model):
    __tablename__ = "users"

    # User info
    id = sqa.Column(sqa.Integer, primary_key=True, index=True)
    email = sqa.Column(sqa.String(80), unique=True, nullable=False)
    username = sqa.Column(sqa.String(100), unique=True, nullable=False)
    password = sqa.Column(sqa.String(100), nullable=False)
    admin = sqa.Column(sqa.Boolean)

    # Relationships
    lists = relationship("List", backref=backref("users"))
    friends = relationship("User",
                           secondary=friends,
                           primaryjoin=id == friends.c.friend1_id,
                           secondaryjoin=id == friends.c.friend2_id,
                           back_populates="friends")
    # outgoing_recommendations = relationship("Recommendation", backref=backref("users"))
    # incoming_recommendations = relationship("Recommendation", backref=backref("users"))
    show_ratings = relationship("Rating", backref=backref("users"))
    alt_show_names = relationship("Show", secondary=alt_names, back_populates="alt_names")

    # Preferences
    names_preference = sqa.Column(sqa.Integer)  # 1 = Japanese, 2 = Romaji, 3 = English (if applicable), 4 = Default (TBA)
    spoiler_preference = sqa.Column(sqa.Integer)  # 1 = Never, 2 = On "seen" shows, 3 = Always
