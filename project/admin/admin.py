from flask import Blueprint, session, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from project.config import settings
from project.automation import migrate_ratings, update_library, add_lists, transfer_shows_to_series
from project.functions import add_to_series

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
    ratings = request.args.get("ratings")
    update = request.args.get("update")
    add_list = request.args.get("list")
    transfer = request.args.get("transfer")
    series_id = request.form.get("seriesID")
    if ratings:
        migrate_ratings()

    if update:
        update_library()

    if add_list:
        add_lists()

    if series_id:
        add_to_series(int(series_id))

    if transfer:
        transfer_shows_to_series()

    if current_user.admin:
        return render_template("/admin/templates/admin/administration.html")
    else:
        return redirect(url_for("community.profile"))
