from flask import render_template, Blueprint, redirect, url_for, request, abort
from flask_login import current_user, login_required
from project.config import settings
from project.models import User, List, Rating, Show, Feedback
import json
from project.automation import migrate_ratings, update_library, add_lists
from project.standalone_functions import assign_data
from project.integrated_functions import collect_feedback, update_feedback_status, update_feedback_note
from project import db

COMMUNITY_BLUEPRINT = Blueprint("community", __name__, template_folder="../../project")

TEMPLATE_PATH = "community/templates/community"


@COMMUNITY_BLUEPRINT.route("/settings")
@login_required
def settings():

    if current_user.is_authenticated:
        return render_template(f"{TEMPLATE_PATH}/settings.html", name=current_user.username)
    else:
        return redirect(url_for("auth.login"))


@COMMUNITY_BLUEPRINT.route("/users/<username>")
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

    return render_template(f"{TEMPLATE_PATH}/profile.html", **variables)


@COMMUNITY_BLUEPRINT.route("/users")
def users():
    users = db.session.query(User).all()
    usernames = [user.username for user in users]

    variables = {
        "usernames": usernames
    }

    return render_template(f"{TEMPLATE_PATH}/users.html", **variables)


@COMMUNITY_BLUEPRINT.route("/friends")
def friends():
    pass


@COMMUNITY_BLUEPRINT.route("/users/<username>/lists/<list_name>")
def list_display(username, list_name):
    user = User.query.filter_by(username=username).first()
    current_list = List.query.filter_by(owner_id=user.id, name=list_name).first()
    if not current_list:
        abort(404)  # Doesn't work

    variables = {
        "shows": current_list.shows
    }

    return render_template(f"{TEMPLATE_PATH}/list_display.html", **variables)


@COMMUNITY_BLUEPRINT.route("/give-feedback", methods=["GET", "POST"])
def give_feedback():
    feedback_alert = request.form.get("feedback-submission")
    if feedback_alert:
        new_feedback = Feedback(
            user_id=current_user.id,
            type=request.form.get("feedback-type"),
            status=1,
            description=request.form.get("feedback-description")
        )
        db.session.add(new_feedback)
        db.session.commit()

    return render_template(f"{TEMPLATE_PATH}/feedback_submission.html")


@COMMUNITY_BLUEPRINT.route("/view-feedback", methods=["GET", "POST"])
def view_feedback():
    status_update = request.form.get("status-select")
    note_update = request.form.get("dev-note")
    feedback_id = request.form.get("feedback-id")
    if status_update:
        update_feedback_status(int(feedback_id), int(status_update))
    if note_update:
        update_feedback_note(int(feedback_id), note_update)
    feedback_list = collect_feedback()

    return render_template(f"{TEMPLATE_PATH}/feedback_list.html", feedback_list=feedback_list)


def assign_values(x_data, y_data):
    pass
