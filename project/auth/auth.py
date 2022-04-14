from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from project.models import User
from project import db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():

    return render_template("auth/templates/auth/login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash("Your login details don't match. Please try again.")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    return redirect(url_for("community.profile"))


@auth.route("/register")
def register():

    return render_template("auth/templates/auth/register.html")


@auth.route("/register", methods=["POST"])
def register_post():

    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        flash("This email is already in use")
        return redirect(url_for("auth.register"))

    new_user = User(email=email, username=username, password=generate_password_hash(password, method="sha256"))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    session.pop("selected_shows", None)
    logout_user()
    return redirect(url_for("main.index"))
