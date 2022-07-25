from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
import project.automation as auto
from project.integrated_functions import update_full_series
import re
from project.models import Update
import datetime as dt
from project import db

ADMIN_BLUEPRINT = Blueprint("admin", __name__, template_folder="../../project")

TEMPLATES_PATH = "/admin/templates/admin"


@ADMIN_BLUEPRINT.route("/edit")
@login_required
def edit():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@ADMIN_BLUEPRINT.route("/warnings")
@login_required
def warnings():
    return """This page is a work in progress. <a href="/display">Go back</a>"""


@ADMIN_BLUEPRINT.route("/administration", methods=["GET", "POST"])
@login_required
def administration():
    if not current_user.admin:
        return redirect(url_for("COMMUNITY_BLUEPRINT.profile"))

    if request.args.get("ratings"):
        auto.migrate_ratings()

    if request.args.get("update"):
        auto.update_library()

    if request.args.get("list"):
        auto.add_lists()

    if request.args.get("transfer"):
        auto.transfer_shows_to_series()

    if request.args.get("migrate"):
        auto.migrate_drama_to_tone()

    series_id = request.form.get("seriesID")
    if series_id:
        update_full_series(int(series_id))

    if request.form.get("submit-update"):
        string_dates = re.split("-", request.form.get("update-date"))
        date = dt.datetime(int(string_dates[0]), int(string_dates[1]), int(string_dates[2]))
        new_update = Update(
            version=request.form.get("version-number"),
            type=request.form.get("update-type"),
            comment=request.form.get("update-description"),
            date=date,
            published=False
        )
        db.session.add(new_update)
        db.session.commit()

    if request.form.get("publish-update"):
        updates_to_publish = Update.query.filter_by(version=request.form.get("published-version")).all()
        for update in updates_to_publish:
            update.published = True
        db.session.commit()

    return render_template(f"{TEMPLATES_PATH}/administration.html")

