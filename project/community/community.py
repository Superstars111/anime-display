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
    data_points = []
    for show_list in user.lists:
        if show_list.name == "Seen":
            for show in show_list.shows:
                rating = Rating.query.filter_by(rater_id=user.id, show_id=show.id).first()
                data_points.append({"x": rating.drama, "y": rating.pacing})
    data_points = json.dumps(data_points)

    variables = {
        "username": username,
        "data_points": data_points,
        "lists": user.lists
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

