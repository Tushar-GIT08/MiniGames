from flask import Blueprint, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import find_user, create_user


auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return render_template("signup.html", error="PLEASE FILL IN ALL FIELDS")

        existing_user = find_user(username, email)

        if existing_user:
            return render_template(
                "signup.html",
                error="YOU ARE ALREADY SIGNED UP. PLEASE LOG IN"
            )

        hashed_password = generate_password_hash(password)

        create_user(username, email, hashed_password)

        return redirect("/login")

    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="PLEASE FILL IN ALL FIELDS")

        user = find_user(username, username)

        if user is None:
            return render_template(
                "login.html",
                error="DETAILS NOT FOUND. PLEASE ENTER CORRECT DETAILS AGAIN OR SIGN UP."
            )

        if check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/mode")

        else:
            return render_template("login.html", error="Incorrect password")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")