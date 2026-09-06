from flask import Blueprint, render_template, session, redirect , request , jsonify
import random

from database.db import(
    get_username


)



memory = Blueprint("memory", __name__)


@memory.route("/memory" , methods=["GET" , "POST"])
def memory_game():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    username = get_username(user_id)




    return render_template(
            "memory.html",
            username=username
        )

