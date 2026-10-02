from flask import Blueprint, render_template, session, redirect , request , jsonify
import random

from database.db import(
    get_username,
    insert_memory,
    get_memory_games

)

memory = Blueprint("memory", __name__)


@memory.route("/memory" , methods=["GET" , "POST"])
def memory_game():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    username = get_username(user_id)

    if request.method == "POST":
        data = request.get_json()

        moves = data["moves"]
        time = data["time"]
        result = data["result"]

        insert_memory(user_id, moves, time, result)

    records = get_memory_games(user_id)

    print(records)

    if records:
        small = records[0][0]

        for i in records:
            if i[0] < small:
                small = i[0]
    else:
        small = None

    return render_template("memory.html",username=username, records=records, small=small)

@memory.route("/memory/reset")
def reset_memory():

    if "user_id" not in session:
        return redirect("/login")
    
    return redirect("/memory")




