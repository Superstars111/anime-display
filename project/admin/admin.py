from flask import Blueprint, session
from flask_login import login_required
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
