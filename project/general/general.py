from flask import Flask, request, render_template, redirect, Blueprint, url_for, session
from flask_login import login_required, current_user, login_user
from project.models import Show
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import decimal as dc
from project import db
from project.config import settings
import json

general = Blueprint("general", __name__, template_folder="../../project")
# app = Flask(__name__)
# app.secret_key = "testing"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///anime-display-users.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# login.init_app(app)
# login.login_view = "login"


# @app.before_first_request
# def create_table():
#     db.create_all()


@general.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("community.settings"))
    else:
        return redirect(url_for("auth.login"))


@general.route("/graph_test", methods=["POST", "GET"])
def graph_test():
    data = [
        {"x": 2, "y": 6},
        {"x": 7, "y": -9},
        {"x": -10, "y": -12},
        {"x": 37, "y": 38},
        {"x": -50, "y": -50},
        {"x": 50, "y": 50}
    ]
    change = request.args.get("change", "")
    if change:
        data = [
            {"x": 23, "y": 40},
            {"x": 32, "y": -23},
            {"x": -30, "y": -10},
            {"x": 2, "y": 3},
            {"x": 50, "y": -50},
            {"x": -50, "y": 50}
        ]
        data = json.dumps(data)
        return data
    else:
        pass
    data = json.dumps(data)
    return render_template("graph_test.html", data_test=data)


@general.errorhandler(404)
def error404(error):
    return """Sorry, but much like Asta's ability to control his volume, this page does not exist. 
    <a href="/display">Go back</a>"""


# def collect_image(show):
#     return f"{show['coverMed']}"
#
#
# def collect_episodes(show):
#     return f"{show['episodes']}"
#
#
# def collect_seasons(show):
#     return f"{show['seasons']}"
#
#
# def collect_movies(show):
#     return f"{show['movies']}"
#
#
# def collect_unaired(show):
#     return f"{show['unairedSeasons']}"
#
#
# def collect_synopsis(show):
#     return show['description']
#
#
# def collect_public_score(show):
#     return f"{show['score']}"


def collect_genres(show):
    pass


def collect_tags(show):
    pass


def collect_warnings(show):
    pass


def collect_spoilers(show):
    pass


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    pass
