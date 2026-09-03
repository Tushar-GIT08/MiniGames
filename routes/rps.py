from flask import Blueprint, request, render_template, session, redirect, jsonify
import random

from database.db import get_game_record, create_record, update_record, get_username

rps = Blueprint("rps", __name__)

@rps.route("/rps", methods=["GET", "POST"])
def play_rps():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    record = get_game_record(user_id, "rps")

    if record is None:
        create_record(user_id, "rps")
        record = (0,0,0)

    if request.method == "POST":

        data = request.get_json()

        choice = data.get("choice")

        all_choices = ["rock", "paper", "scissors"]

        comp_choice = random.choice(all_choices)

        if choice == comp_choice:
            result = "IT'S A DRAW!!"
            db_result = "draw"

        elif (
            (choice == "rock" and comp_choice == "scissors")
            or
            (choice == "paper" and comp_choice == "rock")
            or
            (choice == "scissors" and comp_choice == "paper")
        ):
            result = "YOU WON!!"
            db_result = "win"

        else:
            result = "YOU LOST!!"
            db_result = "loss"

        print(db_result)

        update_record(user_id, "rps", db_result)

        record = get_game_record(user_id, "rps")

        return jsonify({
            "choice":choice,
            "comp_choice":comp_choice,
            "result":result,
            "wins": record[0],
            "losses": record[1],
            "draws": record[2]
        })

    username = get_username(user_id)


    return render_template("rps.html",record=record)