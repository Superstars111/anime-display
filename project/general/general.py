from flask import Flask, request, render_template, redirect, Blueprint, url_for, session
from flask_login import login_required, current_user, login_user
from project.models import Update
import re

GENERAL_BLUEPRINT = Blueprint("general", __name__, template_folder="../../project")
TEMPLATE_PATH = "general/templates/general"


@GENERAL_BLUEPRINT.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("community.settings"))
    else:
        return redirect(url_for("auth.login"))


@GENERAL_BLUEPRINT.route("/updates")
def update_log():
    published_updates = Update.query.filter_by(published=True).all()
    published_updates.sort(key=lambda x: x.date, reverse=True)
    releases = []
    displayed_updates = []
    for update in published_updates:
        update_dict = update.dictify()
        print(update_dict["type"])
        print(re.split(" ", update_dict["type"].lower()))
        update_dict["type"] = "-".join(re.split(" ", update_dict["type"].lower()))
        print(update_dict["type"])
        displayed_updates.append(update_dict)
        if update.version not in releases:
            releases.append(update.version)

    variables = {
        "displayed_updates": displayed_updates,
        "releases": releases
    }
    return render_template(f"{TEMPLATE_PATH}/updates.html", **variables)


@GENERAL_BLUEPRINT.errorhandler(404)
def error404(error):
    return """Sorry, but much like Asta's ability to control his volume, this page does not exist. 
    <a href="/display">Go back</a>""", 404


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    pass
