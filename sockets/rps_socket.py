from flask import session , request
from flask_socketio import emit, join_room
import random
import string
import time

from database.db import get_game_record, create_record, update_record

from sockets.ttt_socket import socketio

rps_games = {}

REJOIN_GRACE_SECONDS = 120
ROOM_TTL_SECONDS = 1800

def generate_room_code():

    char = string.digits
    code = ""

    for i in range(4):
        code += random.choice(char)

    return code


@socketio.on("rps_create_room")
def create_room():

    while True:
        room = generate_room_code()

        if room not in rps_games:
            break
        
    join_room(room)

    player = {"sid": request.sid, "user_id": session["user_id"], 
              "room": room, "connected": True, "disconnected_at": None}

    rps_games[room] = {"players": [player], "choices": {}, "game_started": False}

    emit("rps_room_created", {"room":room})


@socketio.on("rps_join_game")
def join_game(data):

    room = data["room"]

    if room not in rps_games:
        emit("rps_room_not_found", {"message":"room does not exist"})
        return

    for player in rps_games[room]["players"]:
        if player["user_id"] == session["user_id"]:

            if player["connected"]:
                emit("rps_already_joined", {"message":"already joined"})
                return
            
            else: 
                elapsed = time.time() - player["disconnected_at"]

                if elapsed < REJOIN_GRACE_SECONDS:
                    
                    player["sid"] = request.sid
                    player["connected"] = True
                    player["disconnected_at"] = None

                    join_room(room)

                    players = rps_games[room]["players"]

                    for player_new in players:
                        if player_new["sid"] != request.sid:
                            emit("rps_opponent_reconnected",{"message": "Opponent reconnected"},
                                to=player_new["sid"])
                    
                    emit("rps_valid_reconnect", {"message": "You reconnected"}, to=request.sid)
                    return
                
                else:
                    emit("rps_expired", {"message":"grace period expired"})
                    return
            

    if len(rps_games[room]["players"]) >= 2:
        emit("rps_room_full", {"message":"room is full"})
        return

    join_room(room)

    player = {"sid": request.sid, "user_id": session["user_id"], 
              "room": room, "connected": True, "disconnected_at": None}

    rps_games[room]["players"].append(player)

    if len(rps_games[room]["players"]) == 2:
        rps_games[room]["game_started"] = True

        players = rps_games[room]["players"]

        player1 = players[0]
        player2 = players[1]

        emit("rps_game_started", {"message": "Game started", "player": "player1"}, to=player1["sid"])

        emit("rps_game_started", {"message": "Game started","player": "player2"}, to=player2["sid"])

@socketio.on("rps_make_choice")
def make_choice(data):

    choice = data["choice"]

    valid = ["rock", "paper", "scissors"]

    if choice not in valid:
        return

    for room in rps_games:
        for player in rps_games[room]["players"]:

            if player["sid"] == request.sid:
                room = player["room"]

                if not rps_games[room]["game_started"]:
                    return

                if player["sid"] in rps_games[room]["choices"]:
                    return

                rps_games[room]["choices"][player["sid"]] = choice

                if len(rps_games[room]["choices"]) == 2:
                    choices = rps_games[room]["choices"]

                    player_sids = list(choices.keys())

                    player1_choice = choices[player_sids[0]]
                    player2_choice = choices[player_sids[1]]

                    if player1_choice == player2_choice:
                        result = "draw"

                    elif(
                        (player1_choice == "rock" and player2_choice == "scissors") or
                        (player1_choice == "paper" and player2_choice == "rock") or
                        (player1_choice == "scissors" and player2_choice == "paper") 
                    ):
                        result = "player1"

                    else:
                        result = "player2"

                    players = rps_games[room]["players"]

                    player1 = players[0]
                    player1_record = get_game_record(player1["user_id"], "rps")

                    if player1_record is None:
                        create_record(player1["user_id"], "rps")

                    player2 = players[1]
                    player2_record = get_game_record(player2["user_id"], "rps")

                    if player2_record is None:
                        create_record(player2["user_id"], "rps")


                    if result == "player1":
                        player1_result = "win"
                        player2_result = "loss"

                    elif result == "player2":
                        player1_result = "loss"
                        player2_result = "win"

                    else:
                        player1_result = "draw"
                        player2_result = "draw"

                    update_record(player1["user_id"], "rps", player1_result)
                    update_record(player2["user_id"], "rps", player2_result)

                    emit("rps_round_result", {"player1_choice": player1_choice,
                                          "player2_choice": player2_choice,
                                          "player1_result": player1_result,
                                          "player2_result": player2_result}, to=room)
                    
                    choices.clear()

@socketio.on("disconnect")
def disconnect():

    for room in rps_games:
        for player in rps_games[room]["players"]:

            if player["sid"] == request.sid:

                player["sid"] = None
                player["connected"] = False
                player["disconnected_at"] = time.time()
                
                emit("opponent_disconnected",{"message": "Opponent disconnected"},to=room)
                break





