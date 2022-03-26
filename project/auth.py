from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import UserModel
from . import db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    # if current_user.is_authenticated:
    #     return redirect("/display_all")
    #
    # if request.method == "POST":
    #     email = request.form["email"]
    #     user = UserModel.query.filter_by(email=email).first()
    #     if user is not None and user.check_password(request.form["password"]):
    #         login_user(user)
    #         return redirect("/display_all")

    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = UserModel.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash("Your login details don't match. Please try again.")
        return redirect(url_for("auth.login"))

    return redirect(url_for("main.profile"))


@auth.route("/register")
def register():
    # if current_user.is_authenticated:
    #     return redirect("/display_all")
    #
    # if request.method == "POST":
    #     email = request.form["email"]
    #     username = request.form["username"]
    #     password = request.form["password"]
    #
    #     if UserModel.query.filter_by(email=email):
    #         return "Sorry, this email address is already in use."
    #
    #     user = UserModel(email=email, username=username)
    #     user.set_password(password)
    #     db.session.add(user)
    #     db.session.commit()
    #     return redirect("/login")

    return render_template("register.html")


@auth.route("/register", methods=["POST"])
def register_post():

    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    user = UserModel.query.filter_by(email=email).first()

    if user:
        flash("This email is already in use")
        return redirect(url_for("auth.register"))

    new_user = UserModel(email=email, username=username, password=generate_password_hash(password, method="sha256"))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    pass
