from flask import Flask, request, render_template, session, redirect, jsonify
import os
from dotenv import load_dotenv

from database.db import init_db, find_user, create_user
from routes.auth import auth
from routes.games import games
from routes.rps import rps
from routes.hangman import hangman
from routes.tictactoe import tictactoe

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(auth)
app.register_blueprint(games)
app.register_blueprint(rps)
app.register_blueprint(hangman)
app.register_blueprint(tictactoe)


if __name__ == "__main__":

    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)