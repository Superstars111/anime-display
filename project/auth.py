from flask import Blueprint, render_template
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


@auth.route("/logout")
def logout():
    pass
