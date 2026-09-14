from flask import Blueprint, render_template, session, redirect
from database.db import get_game_record, get_username

ttt_multiplayer = Blueprint("ttt_multiplayer", __name__)

@ttt_multiplayer.route("/tictactoe/2p")
def multiplayer_game():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    username = get_username(user_id)
    record = get_game_record(user_id, "tictactoe")

    return render_template("tictactoe.html",mode="2p",username=username,record=record)