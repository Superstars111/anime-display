from flask import render_template, Blueprint, redirect, url_for, request, abort
from flask_login import current_user, login_required
from project.config import settings
from project.models import User, List, Rating, Show, Feedback
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

    return render_template(f"{template_path}/list_display.html", **variables)


@community.route("/give-feedback", methods=["GET", "POST"])
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

    return render_template(f"{template_path}/feedback_submission.html")


@community.route("/view-feedback")
def view_feedback():
    feedback_list = []
    for feedback_item in db.session.query(Feedback).all():

        user = User.query.filter_by(id=feedback_item.user_id).first()

        if feedback_item.type == 1:
            feedback_type = "Bug Report"
        elif feedback_item.type == 2:
            feedback_type = "Feature Request"
        elif feedback_item.type == 3:
            feedback_type = "Data Request"
        else:
            feedback_type = "Other Feedback"

        if feedback_item.status == 1:
            feedback_status = "New Feedback"
        elif feedback_item.status == 2:
            feedback_status = "Planned"
        elif feedback_item.status == 3:
            feedback_status = "In Progress"
        else:
            feedback_status = "Closed"

        feedback_list.append({
            "user": user.username,
            "type": feedback_type,
            "status": feedback_status,
            "description": feedback_item.description,
            "note": feedback_item.note
        })

    return render_template(f"{template_path}/feedback_list.html", feedback_list=feedback_list)


def assign_values(x_data, y_data):
    pass
