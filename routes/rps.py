from flask import Blueprint, request, render_template, session, redirect
import random

rps = Blueprint("rps", __name__)

@rps.route("/rps", methods=["GET", "POST"])
def play_rps():

    if "user_id" not in session:
        return redirect("/login")

    choice = ""
    comp_choice = ""
    result = ""

    if request.method == "POST":

        choice = request.form.get("choice")

        all_choices = ["rock", "paper", "scissors"]

        comp_choice = random.choice(all_choices)

        if choice == comp_choice:
            result = "IT'S A DRAW!!"

        elif (
            (choice == "rock" and comp_choice == "scissors")
            or
            (choice == "paper" and comp_choice == "rock")
            or
            (choice == "scissors" and comp_choice == "paper")
        ):
            result = "YOU WON!!"

        else:
            result = "YOU LOST!!"

        print(choice, comp_choice)

    return render_template(
        "rps.html",
        choice=choice,
        comp_choice=comp_choice,
        result=result
    )