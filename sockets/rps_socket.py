from flask import session , request
from flask_socketio import emit, join_room
from sockets.core import socketio, register_rooms, generate_room_code, REJOIN_GRACE_SECONDS
import random
import string
import time

from database.db import get_game_record, create_record, update_record

from sockets.core import socketio, register_rooms

rps_games = {}
register_rooms(rps_games)


@socketio.on("rps_create_room")
def create_room():

    room = generate_room_code()
        
    join_room(room)

    player = {"sid": request.sid, "user_id": session["user_id"], 
              "room": room, "connected": True, "disconnected_at": None}

    rps_games[room] = {"players": [player], "choices": {}, "last_round": None,
                        "score": {"player1": 0, "player2": 0}, "game_started": False,
                        "last_activity_at": time.time()}

    emit("rps_room_created", {"room":room})


@socketio.on("rps_join_game")
def join_game(data):

    room = data["room"]

    if room not in rps_games:
        emit("rps_room_not_found", {"message":"room does not exist"})
        return

    rps_games[room]["last_activity_at"] = time.time()

    for player in rps_games[room]["players"]:
        if player["user_id"] == session["user_id"]:

            game = rps_games[room]

            
            if not game["game_started"]:
                emit("rps_already_joined", {"message": "already joined"})
                return

            if not player["connected"]:
                if time.time() - player["disconnected_at"] >= REJOIN_GRACE_SECONDS:
                    emit("rps_expired", {"message": "grace period expired"})
                    return

            was_notified = player.get("notified", False)

            player["sid"] = request.sid
            player["connected"] = True
            player["disconnected_at"] = None
            player["notified"] = False

            join_room(room)

            players = game["players"]

            if was_notified:
                for other in players:
                    if other is not player and other["sid"]:
                        emit("rps_opponent_reconnected", {"message": "Opponent reconnected"}, to=other["sid"])

            role = "player1" if players[0] is player else "player2"

            emit("rps_valid_reconnect", {
                "player": role,
                "my_choice": game["choices"].get(player["user_id"]),
                "opponent_chose": any(uid != player["user_id"] for uid in game["choices"]),
                "last_round": game["last_round"],
                "score": game["score"]
            }, to=request.sid)
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
                rps_games[room]["last_activity_at"] = time.time()

                if not rps_games[room]["game_started"]:
                    return

                if player["user_id"] in rps_games[room]["choices"]:
                    return

                rps_games[room]["choices"][player["user_id"]] = choice

                choices = rps_games[room]["choices"]

                players = rps_games[room]["players"]

                if len(choices) == 1:
                    rps_games[room]["last_round"] = None
                    for abc in players:
                        if abc["user_id"] not in choices and abc["sid"]:
                            emit("rps_opponent_made_choice", {}, to=abc["sid"])


                if len(rps_games[room]["choices"]) == 2:

                    player1_choice = choices[players[0]["user_id"]]
                    player2_choice = choices[players[1]["user_id"]]

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

                    if result == "player1":
                        rps_games[room]["score"]["player1"] += 1
                    elif result == "player2":
                        rps_games[room]["score"]["player2"] += 1

                    round_data = {"player1_choice": player1_choice,
                                  "player2_choice": player2_choice,
                                  "player1_result": player1_result,
                                  "player2_result": player2_result,
                                  "score": dict(rps_games[room]["score"])}

                    rps_games[room]["last_round"] = round_data

                    emit("rps_round_result", round_data, to=room)   

                    choices.clear()







