from flask import Blueprint, request, render_template, session, redirect, jsonify
import random


hangman = Blueprint("hangman", __name__)


words = [
    "planet", "coffee", "laptop", "python", "rocket",
    "forest", "guitar", "castle", "puzzle", "camera",
    "school", "window", "dragon", "island", "summer",
    "orange", "keyboard", "monster", "diamond", "thunder"
]


@hangman.route("/hangman", methods=["GET", "POST"])
def play_hangman():

    if "user_id" not in session:
        return redirect("/login")

    # Start a new game if there is no game currently running
    if "word" not in session:
        session["word"] = random.choice(words)
        session["guessed_letters"] = []
        session["wrong_guesses"] = 0

    word = session["word"]

    # POST
    if request.method == "POST":

        data = request.get_json()
        guess = data["guess"]

        guessed_letters = session["guessed_letters"]

        if guess not in guessed_letters:

            guessed_letters.append(guess)
            session["guessed_letters"] = guessed_letters

            if guess not in word:
                session["wrong_guesses"] += 1

        hidden_word = ""

        for i in word:

            if i in session["guessed_letters"]:
                hidden_word += i + " "
            else:
                hidden_word += "_ "

        game_over = False

        if "_" not in hidden_word:
            game_over = True

        if session["wrong_guesses"] >= 5:
            game_over = True

        return jsonify({
            "hidden_word": hidden_word,
            "wrong_guesses": session["wrong_guesses"],
            "game_over": game_over,
            "word": word
        })

    # GET
    hidden_word = ""

    for i in word:

        if i in session["guessed_letters"]:
            hidden_word += i + " "
        else:
            hidden_word += "_ "

    return render_template(
        "hangman.html",
        hidden_word=hidden_word,
        wrong_guesses=session["wrong_guesses"]
    )


@hangman.route("/reset")
def reset():

    session.pop("guessed_letters", None)
    session.pop("wrong_guesses", None)
    session.pop("word", None)

    return redirect("/hangman")