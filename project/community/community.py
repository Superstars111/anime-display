from flask import render_template, Blueprint, redirect, url_for, request
from flask_login import current_user, login_required
from project.config import settings
from project.models import User, List, Rating, Show
import json

community = Blueprint("community", __name__, template_folder="../../project")


@community.route("/settings")
@login_required
def settings():

    ratings = request.args.get("ratings")
    if ratings:
        for rating in current_user.show_ratings:
            print(rating.score)

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
        "data_points": data_points
    }

    return render_template("community/templates/community/profile.html", **variables)
