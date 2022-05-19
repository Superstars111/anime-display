from flask import render_template, Blueprint, redirect, url_for, request, abort
from flask_login import current_user, login_required
from project.config import settings
from project.models import User, List, Rating, Show
import json
from project.automation import migrate_ratings, update_library, add_lists
from project.standalone_functions import assign_data
from project import db

community = Blueprint("community", __name__, template_folder="../../project")

template_path = "community/templates/community"


@community.route("/settings")
@login_required
def settings():

    if current_user.is_authenticated:
        return render_template("community/templates/community/settings.html", name=current_user.username)
    else:
        return redirect(url_for("auth.login"))


@community.route("/users/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()

    x_data = request.args.get("x-coord", "")
    y_data = request.args.get("y-coord", "")
    data = assign_data(user.show_ratings, x_data, y_data)
    if x_data or y_data:
        return data

    variables = {
        "username": username,
        "data": data,
        "lists": user.lists,
        "url": f"/users/{username}"
    }

    return render_template("community/templates/community/profile.html", **variables)


@community.route("/users")
def users():
    users = db.session.query(User).all()
    usernames = [user.username for user in users]

    variables = {
        "usernames": usernames
    }

    return render_template(f"{template_path}/users.html", **variables)


@community.route("/friends")
def friends():
    pass


@community.route("/users/<username>/lists/<list_name>")
def list_display(username, list_name):
    user = User.query.filter_by(username=username).first()
    current_list = List.query.filter_by(owner_id=user.id, name=list_name).first()
    if not current_list:
        abort(404)  # Doesn't work

    variables = {
        "shows": current_list.shows
    }

    return render_template("community/templates/community/list_display.html", **variables)


def assign_values(x_data, y_data):
    pass
