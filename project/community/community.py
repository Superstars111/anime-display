from flask import render_template, Blueprint, redirect, url_for
from flask_login import current_user, login_required
from project.config import settings

community = Blueprint("community", __name__, template_folder="../../project")


@community.route("/settings")
@login_required
def settings():
    if current_user.is_authenticated:
        return render_template("community/templates/community/settings.html", name=current_user.username)
    else:
        return redirect(url_for("auth.login"))


@community.route("/users/<username>")
def profile(username):
    return render_template("community/templates/community/profile.html", username=username)
