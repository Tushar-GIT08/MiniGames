from flask import Flask, request, render_template, session, redirect, jsonify

import os, random, string

from dotenv import load_dotenv

from database.db import init_db, find_user, create_user
from routes.auth import auth
from routes.games import games
from routes.rps import rps
from routes.hangman import hangman
from routes.tictactoe import tictactoe
from routes.memory import memory

from routes.rps_multiplayer import rps_multiplayer
from routes.ttt_multiplayer import ttt_multiplayer

from sockets import rps_socket
from sockets.ttt_socket import socketio, cleanup_loop

load_dotenv()

app = Flask(__name__)
socketio.init_app(app)

app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(auth)
app.register_blueprint(games)
app.register_blueprint(rps)
app.register_blueprint(hangman)
app.register_blueprint(tictactoe)
app.register_blueprint(memory)

app.register_blueprint(rps_multiplayer)
app.register_blueprint(ttt_multiplayer)


if __name__ == "__main__":
    init_db()
    socketio.start_background_task(cleanup_loop)
    socketio.run(app, debug=True, use_reloader=False)
  