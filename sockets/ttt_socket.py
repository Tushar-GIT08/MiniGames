from flask import session, request
from flask_socketio import join_room, emit, SocketIO
import random
import string

from database.db import update_record

socketio = SocketIO()

game_states = {}

def generate_room_code():

    characters = string.digits

    code = ""

    for i in range(4):
        code += random.choice(characters)

    return code

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

@socketio.on("join_game")
def handle_join_game(data):

    room = data["room"]

    if room not in game_states:
        emit("room_not_found",{"message":"room does not exist"})
        return

    if len(game_states[room]["players"]) >= 2:
        emit("room_full", {"message":"room is full"})
        return

    join_room(room)

    first_player_symbol = game_states[room]["players"][0]["symbol"]

    if first_player_symbol == "X":
        symbol = "O"
    else:
        symbol = "X"

    player = {"sid": request.sid , "symbol": symbol, "user_id":session["user_id"]}

    game_states[room]["players"].append(player)

    emit("player_assigned", {"symbol": symbol})

    if len(game_states[room]["players"]) == 2:
        game_states[room]["game_started"] = True

        emit("game_started", {"message": "Game started", "turn": "X"}, to=room)

@socketio.on("create_room")
def handle_create_room():

    while True:

        room = generate_room_code()

        if room not in game_states:
            break

    game_states[room] = {"board": "_________","players": [],"turn": "X","game_started": False,
                        "game_over": False,"rematch_request": None}

    join_room(room)

    symbol = random.choice(["X", "O"])

    game_states[room]["players"].append({"sid": request.sid,"symbol": symbol,"user_id": session["user_id"]})

    emit("room_created", {"room": room,"symbol": symbol})

@socketio.on("make_move")
def handle_make_move(data):

    room = data["room"]
    position = data["position"]

    current_room = game_states[room]

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

@socketio.on("request_rematch")
def handle_request_rematch(data):

    room = data["room"]

    current_room = game_states[room]

    if current_room["rematch_request"] is not None:
        return

    current_room["rematch_request"] = request.sid

    emit("rematch_requested", {"message": "Player wants to start a new game"}, to=room, include_self=False)

@socketio.on("rematch_response")
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

        if request.sid == current_room["rematch_request"]:
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

@socketio.on("disconnect")
def handle_disconnect():

    for room in game_states:
        current_room = game_states[room]

        for player in current_room["players"]:

            if player["sid"] == request.sid:
                current_room["players"].remove(player)

                emit("opponent_disconnected",{"message": "Opponent disconnected"},to=room)
                break
