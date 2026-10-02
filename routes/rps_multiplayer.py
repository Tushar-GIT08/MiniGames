from flask import Blueprint, render_template, session, redirect
from database.db import get_game_record, get_username

rps_multiplayer = Blueprint("rps_multiplayer", __name__)

@rps_multiplayer.route("/rps/2p")
def multiplayer_game():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    username = get_username(user_id)
    record = get_game_record(user_id, "rps")

    return render_template("rps.html",mode="2p",username=username,record=record)
