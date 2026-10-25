from flask import Blueprint, render_template, session, redirect
from database.db import get_username

memory_multiplayer = Blueprint("memory_multiplayer", __name__)

@memory_multiplayer.route("/memory/2p")
def multiplayer_game():

    if "user_id" not in session:
        return redirect("/login")

    username = get_username(session["user_id"])

    return render_template("memory_multiplayer.html", username=username)