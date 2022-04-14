from flask import render_template, Blueprint
from flask_login import current_user, login_required
from project.config import settings

community = Blueprint("community", __name__, template_folder="../../project")


@community.route("/settings")
@login_required
def settings():
    return render_template("community/templates/community/profile.html", name=current_user.username)


@community.route("/users/<username>")
def profile(username):
    pass
