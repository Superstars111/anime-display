from flask import Blueprint, session, render_template, redirect, url_for
from flask_login import login_required, current_user
from project.config import settings

admin = Blueprint("admin", __name__, template_folder="../../project")


@admin.route("/edit")
@login_required
def edit():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@admin.route("/warnings")
@login_required
def warnings():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@admin.route("/administration")
@login_required
def administration():
    if current_user.admin:
        return render_template("/admin/templates/admin/administration.html")
    else:
        return redirect(url_for("community.profile"))
