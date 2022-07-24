from flask import Flask, request, render_template, redirect, Blueprint, url_for, session
from flask_login import login_required, current_user, login_user

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
    return render_template(f"{TEMPLATE_PATH}/updates.html")


@GENERAL_BLUEPRINT.errorhandler(404)
def error404(error):
    return """Sorry, but much like Asta's ability to control his volume, this page does not exist. 
    <a href="/display">Go back</a>""", 404


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    pass
