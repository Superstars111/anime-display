from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from project.models import User, List
from project import db

AUTH_BLUEPRINT = Blueprint("auth", __name__)

TEMPLATE_PATH = "auth/templates/auth"


@AUTH_BLUEPRINT.route("/login")
def login():

    return render_template(f"{TEMPLATE_PATH}/login.html")


@AUTH_BLUEPRINT.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash("Your login details don't match. Please try again.")
        return redirect(url_for("AUTH_BLUEPRINT.login"))

    login_user(user, remember=remember)
    return redirect(f"/users/{user.username}")


@AUTH_BLUEPRINT.route("/register")
def register():

    return render_template(f"{TEMPLATE_PATH}/register.html")


@AUTH_BLUEPRINT.route("/register", methods=["POST"])
def register_post():

    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        flash("This email is already in use")
        return redirect(url_for("AUTH_BLUEPRINT.register"))

    new_user = User(email=email, username=username, password=generate_password_hash(password, method="sha256"))
    db.session.add(new_user)
    db.session.commit()

    seen_list = List(owner_id=new_user.id, name="Seen")
    to_watch_list = List(owner_id=new_user.id, name="To Watch")
    partially_seen_list = List(owner_id=new_user.id, name="Partially Seen")

    db.session.add_all([seen_list, to_watch_list, partially_seen_list])
    db.session.commit()

    return redirect(url_for("AUTH_BLUEPRINT.login"))


@AUTH_BLUEPRINT.route("/logout")
@login_required
def logout():
    session.pop("selected_shows", None)
    logout_user()
    return redirect(url_for("GENERAL_BLUEPRINT.index"))
