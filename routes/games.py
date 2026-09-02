from flask import Blueprint, render_template, session, redirect


games = Blueprint("games", __name__)


@games.route("/")
def home():

    return render_template("landing.html")


@games.route("/games")
def game_menu():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("index.html")