from flask import Flask, request, render_template, redirect, Blueprint, url_for, session
from flask_login import login_required, current_user, login_user
from project.models import Update
import re
import random

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
        update_dict["type"] = "-".join(re.split(" ", update_dict["type"].lower()))
        displayed_updates.append(update_dict)
        if update.version not in releases:
            releases.append(update.version)

    variables = {
        "displayed_updates": displayed_updates,
        "releases": releases
    }
    return render_template(f"{TEMPLATE_PATH}/updates.html", **variables)


@GENERAL_BLUEPRINT.app_errorhandler(404)
def error404(error):
    things_that_dont_exist = [
        "Asta's ability to control his volume",
        "No Game No Life Season 2",
        "the ending for Hunter x Hunter",
        "your sense of dignity while watching Domestic Girlfriend",
        "Eren's mom's life",
        "Endeavor's right to be the #1 hero",
        "Goku's limits"
    ]
    thing_var = random.choices(things_that_dont_exist)[0]
    return render_template(f"{TEMPLATE_PATH}/404.html", thing_var=thing_var), 404


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    pass
