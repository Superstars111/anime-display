from flask import render_template, Blueprint, redirect, url_for, request
from flask_login import current_user, login_required
from project.config import settings
from project.models import User, List, Rating, Show
import json
from project.automation import migrate_ratings, update_library, add_lists

community = Blueprint("community", __name__, template_folder="../../project")


@community.route("/settings")
@login_required
def settings():

    # Automated tasks- eventually won't be needed
    ratings = request.args.get("ratings")
    update = request.args.get("update")
    add = request.args.get("list")
    if ratings:
        migrate_ratings()

    if update:
        update_library()

    if add:
        add_lists()

    if current_user.is_authenticated:
        return render_template("community/templates/community/settings.html", name=current_user.username)
    else:
        return redirect(url_for("auth.login"))


@community.route("/users/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()
    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = assign_data(user, x_data, y_data)
    if x_data or y_data:
        return data
    # for show_list in user.lists:
    #     if show_list.name == "Seen":
    #         for show in show_list.shows:
    #             rating = Rating.query.filter_by(user_id=user.id, show_id=show.id).first()
    #             data.append({"x": rating.drama, "y": rating.pacing})
    # data = json.dumps(data)

    variables = {
        "username": username,
        "data": data,
        "lists": user.lists,
        "url": f"/users/{username}"
    }

    return render_template("community/templates/community/profile.html", **variables)


@community.route("/users/<username>/lists/<list_name>")
def list_display(username, list_name):
    user = User.query.filter_by(username=username).first()
    current_list = List.query.filter_by(owner_id=user.id, name=list_name).first()
    if not current_list:
        return redirect(url_for("404"))

    variables = {
        "shows": current_list.shows
    }

    return render_template("community/templates/community/list_display.html", **variables)


def assign_data(user, x_data, y_data):
    pacing_scores = []
    tone_scores = []
    energy_scores = []
    fantasy_scores = []
    abstraction_scores = []
    propriety_scores = []
    data = []

    for rating in user.show_ratings:
        pacing_scores.append(rating.pacing)
        tone_scores.append(rating.drama)
        energy_scores.append(rating.energy)
        fantasy_scores.append(rating.fantasy)
        abstraction_scores.append(rating.abstraction)
        propriety_scores.append(rating.propriety)

    if x_data == "tone":
        x = tone_scores
    elif x_data == "energy":
        x = energy_scores
    elif x_data == "fantasy":
        x = fantasy_scores
    elif x_data == "abstraction":
        x = abstraction_scores
    elif x_data == "propriety":
        x = propriety_scores
    else:
        x = pacing_scores

    if y_data == "pacing":
        y = pacing_scores
    elif y_data == "energy":
        y = energy_scores
    elif y_data == "fantasy":
        y = fantasy_scores
    elif y_data == "abstraction":
        y = abstraction_scores
    elif y_data == "propriety":
        y = propriety_scores
    else:
        y = tone_scores

    for idx, rank in enumerate(x):
        point = {
            "x": rank,
            "y": y[idx]
        }
        if type(point["x"]) == int and type(point["y"]) == int:
            data.append(point)

    data = json.dumps(data)

    return data


def assign_values(x_data, y_data):
    pass
