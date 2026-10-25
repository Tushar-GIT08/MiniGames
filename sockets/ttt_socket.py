from flask import session, request
from flask_socketio import join_room, emit
from sockets.core import socketio, register_rooms, generate_room_code, REJOIN_GRACE_SECONDS
import random
import time

from database.db import update_record

game_states = {}
register_rooms(game_states)

def check_winner(board, symbol):

    winning_patterns = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [6, 4, 2]
    ]

    for pattern in winning_patterns:

        if board[pattern[0]] == symbol and \
           board[pattern[1]] == symbol and \
           board[pattern[2]] == symbol:

            return True

    return False

@socketio.on("ttt_join_game")
def handle_join_game(data):

    room = data["room"]

    if room not in game_states:
        emit("room_not_found",{"message":"room does not exist"})
        return

    user_id = session["user_id"]

    for player in game_states[room]["players"]:
        if player["user_id"] == user_id:

            current_room = game_states[room]

            if not current_room["game_started"]:
                emit("already_joined", {"message": "already joined"})
                return

            if not player["connected"]:
                if time.time() - player["disconnected_at"] >= REJOIN_GRACE_SECONDS:
                    emit("rejoin_expired", {"message": "Too much time passed, room is no longer joinable"})
                    return

            was_notified = player.get("notified", False)

            player["sid"] = request.sid
            player["connected"] = True
            player["disconnected_at"] = None
            player["notified"] = False

            join_room(room)

            current_room["last_activity_at"] = time.time()

            if was_notified:
                for other in current_room["players"]:
                    if other is not player and other["sid"]:
                        emit("opponent_reconnected", {"message": "Opponent reconnected"}, to=other["sid"])

            emit("game_state", {"board": current_room["board"],
                                "turn": current_room["turn"],
                                "game_started": current_room["game_started"],
                                "game_over": current_room["game_over"],
                                "rematch_pending": (current_room["rematch_request"] is not None
                                                and current_room["rematch_request"] != user_id),
                                "symbol": player["symbol"]})

            return

    if len(game_states[room]["players"]) >= 2:

        emit("room_full", {"message": "room is full"})
        return

    join_room(room)

    game_states[room]["last_activity_at"] = time.time()


    first_player_symbol = game_states[room]["players"][0]["symbol"]

    if first_player_symbol == "X":
        symbol = "O"
    else:
        symbol = "X"

    player = {"sid": request.sid , "symbol": symbol, "user_id":session["user_id"],
               "connected": True, "disconnected_at": None}

    game_states[room]["players"].append(player)

    emit("player_assigned", {"symbol": symbol})

    if len(game_states[room]["players"]) == 2:
        game_states[room]["game_started"] = True

        emit("game_started", {"message": "Game started", "turn": "X"}, to=room)

@socketio.on("ttt_create_room")
def handle_create_room():

    while True:

        room = generate_room_code()

        if room not in game_states:
            break

    game_states[room] = {"board": "_________","players": [],"turn": "X","game_started": False,
                        "game_over": False,"rematch_request": None, "created_at": time.time(), 
                        "last_activity_at": time.time(),
                        "host_user_id": session["user_id"],
                        }

    join_room(room)

    symbol = random.choice(["X", "O"])

    game_states[room]["players"].append({"sid": request.sid,"symbol": symbol,
                                         "user_id": session["user_id"],"connected": True,
                                         "disconnected_at": None})

    emit("room_created", {"room": room,"symbol": symbol})

@socketio.on("ttt_make_move")
def handle_make_move(data):

    room = data["room"]

    position = data["position"]

    current_room = game_states[room]

    current_room["last_activity_at"] = time.time()

    if not current_room["game_started"]:
        return

    if current_room["game_over"]:
        return

    player_symbol = None

    for player in current_room["players"]:
        if player["sid"] == request.sid:
            player_symbol = player["symbol"]

    turn = current_room["turn"]

    if player_symbol != turn:
        return

    board = current_room["board"]

    if position < 0 or position > 8:
        return

    if board[position] != "_":
        return
    
    board = board[:position] + player_symbol + board[position + 1:]

    current_room["board"] = board

    if check_winner(board, player_symbol):

        winner = None
        loser = None

        for player in current_room["players"]:
            if player["symbol"] == player_symbol:
                winner = player
            else:
                loser = player

        update_record(winner["user_id"], "tictactoe", "win")
        update_record(loser["user_id"], "tictactoe", "loss")

        current_room["game_over"] = True

        emit("game_over" ,{"board": board,"winner": player_symbol}, to=room)
        return

    if "_" not in board:
  
        for player in current_room["players"]:
            update_record(player["user_id"], "tictactoe", "draw")

        current_room["game_over"] = True

        emit("game_over", {"board": board,"winner": "draw"}, to=room)
        return


    if player_symbol == "X":
        current_room["turn"] = "O"
    else:
        current_room["turn"] = "X"

    emit("board_update", {"board": board , "turn": current_room["turn"]}, to=room)

@socketio.on("ttt_request_rematch")
def handle_request_rematch(data):

    room = data["room"]

    current_room = game_states[room]

    if current_room["rematch_request"] is not None:
        return

    current_room["rematch_request"] = session["user_id"]

    emit("rematch_requested", {"message": "Player wants to start a new game"}, to=room, include_self=False)

@socketio.on("ttt_rematch_response")
def handle_rematch_response(data):

    room = data["room"]
    response = data["response"]

    current_room = game_states[room]

    if current_room["rematch_request"] is None:
        return

    if response == "decline":
        current_room["rematch_request"] = None

        emit("rematch_declined", {"message": "Rematch declined"}, to=room)
        return

    if response == "accept":

        if session["user_id"] == current_room["rematch_request"]:
            return

        current_room["board"] = "_________"
        current_room["game_over"] = False
        current_room["rematch_request"] = None

        first_symbol = random.choice(["X", "O"])

        if first_symbol == "X":
            second_symbol = "O"
        else:
            second_symbol = "X"

        current_room["players"][0]["symbol"] = first_symbol
        current_room["players"][1]["symbol"] = second_symbol

        current_room["turn"] = "X"

        for player in current_room["players"]:
            emit("rematch_accepted",{"message": "New game started","turn": "X",
                    "symbol": player["symbol"]},to=player["sid"])

        return

