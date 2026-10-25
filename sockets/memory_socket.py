from flask import session , request
from flask_socketio import emit, join_room
from sockets.core import socketio, register_rooms, generate_room_code, REJOIN_GRACE_SECONDS
import random
import time

memory_games = {}

register_rooms(memory_games)

CARD_ELEMENTS = ["🤓", "💩", "🥸", "🥵", "😂", "😭", "😈", "🤬"]

def new_board():
    board = CARD_ELEMENTS * 2
    random.shuffle(board)
    return board

def build_visible_board(game):
    visible_board = []

    for i in range(len(game["board"])):
        if i in game["matched"] or i in game["revealed"]:
            visible_board.append(game["board"][i])
        else:
            visible_board.append(None)

    return visible_board

def hide_mismatched_cards(room, first, second, current_player, version):
    socketio.sleep(1.2)

    if room not in memory_games:
        return

    game = memory_games[room]

    if game["version"] != version:
        return

    remaining = []

    for position in game["revealed"]:
        if position != first and position != second:
            remaining.append(position)

    game["revealed"] = remaining
    game["flipped_cards"] = []
    game["resolving_turn"] = False

    if current_player == "player1":
        game["current_player"] = "player2"
    else:
        game["current_player"] = "player1"

    visible_board = []

    for i in range(len(game["board"])):
        if i in game["matched"] or i in game["revealed"]:
            visible_board.append(game["board"][i])
        else:
            visible_board.append(None)

    socketio.emit("memory_board_updated", {"board": visible_board,"matched": game["matched"],
                                           "revealed": game["revealed"],
                                           "current_player": game["current_player"],
                                            "scores": game["scores"]
                                            }, to=room)

def send_board_update(room, game):
    visible_board = []

    for i in range(len(game["board"])):
        if i in game["matched"] or i in game["revealed"]:
            visible_board.append(game["board"][i])
        else:
            visible_board.append(None)

    socketio.emit("memory_board_updated", {"board": visible_board,"matched": game["matched"],
                                            "revealed": game["revealed"],
                                            "current_player": game["current_player"],
                                            "scores": game["scores"]
                                            }, to=room)    

@socketio.on("memory_create_room")
def create_room():

    room = generate_room_code()
        
    join_room(room)

    player = {"sid": request.sid, "user_id": session["user_id"], 
              "room": room, "connected": True, "disconnected_at": None}

    memory_games[room] = {"players": [player], "board": [], "matched": [], "revealed": [],
                            "current_player": "player1", "scores": {"player1": 0, "player2": 0},
                            "game_started": False, "game_over": False, "flipped_cards": [],
                             "resolving_turn": False, "rematch_request": None,
                              "starter":"player1", "version": 0,
                               "last_activity_at": time.time() }

    emit("memory_room_created", {"room":room})

@socketio.on("memory_join_game")
def join_game(data):

    room = data["room"]

    if room not in memory_games:
        emit("memory_room_not_found", {"message":"room does not exist"})
        return

    memory_games[room]["last_activity_at"] = time.time()

    for player in memory_games[room]["players"]:
        if player["user_id"] == session["user_id"]:

            game = memory_games[room]

            if not game["game_started"] and player["connected"]:
                emit("memory_already_joined", {"message": "already joined"})
                return

            if not player["connected"]:
                if time.time() - player["disconnected_at"] >= REJOIN_GRACE_SECONDS:
                    emit("memory_expired", {"message": "grace period expired"})
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
                        emit("memory_opponent_reconnected", {"message": "Opponent reconnected"}, to=other["sid"])

            role = "player1" if players[0] is player else "player2"

            visible_board = []

            for i in range(len(game["board"])):
                if i in game["matched"] or i in game["revealed"]:
                    visible_board.append(game["board"][i])
                else:
                    visible_board.append(None)


            emit("memory_valid_reconnect", {"player": role,"board": visible_board,
                                            "matched": game["matched"],
                                            "revealed": game["revealed"],
                                            "current_player": game["current_player"],
                                            "scores": game["scores"],
                                            "game_started": game["game_started"],
                                            "game_over": game["game_over"],
                                            "rematch_pending": (game["rematch_request"] is not None
                                            and game["rematch_request"] != player["user_id"]),
                                            }, to=request.sid)
            return
            

    if len(memory_games[room]["players"]) >= 2:
        emit("memory_room_full", {"message":"room is full"})
        return

    join_room(room)

    player = {"sid": request.sid, "user_id": session["user_id"], 
              "room": room, "connected": True, "disconnected_at": None}

    memory_games[room]["players"].append(player)

    if len(memory_games[room]["players"]) == 2:

        game = memory_games[room]
        game["board"] = new_board()

        game["starter"] = random.choice(["player1","player2"])
        game["current_player"] = game["starter"]

        game["game_started"] = True

        players = game["players"]
        
        player1 = players[0]
        player2 = players[1]

        visible_board = []

        for i in range(len(game["board"])):
            if i in game["matched"] or i in game["revealed"]:
                visible_board.append(game["board"][i])
            else:
                visible_board.append(None)

        game_data = {
            "board": visible_board,
            "matched": game["matched"],
            "revealed": game["revealed"],
            "current_player": game["current_player"],
            "scores": game["scores"],
            "game_started": game["game_started"],
            "game_over": game["game_over"]
        }

        emit("memory_game_started", {"message": "Game started","player": "player1",
            **game_data
        }, to=player1["sid"])

        emit("memory_game_started", {"message": "Game started","player": "player2",
            **game_data
        }, to=player2["sid"])


@socketio.on("memory_flip_card")
def flip_card(data):
    position = data["position"]

    room = None
    player = None

    for room_code in memory_games:
        game = memory_games[room_code]

        for current in game["players"]:
            if current["sid"] == request.sid:
                room = room_code
                player = current
                break

        if player is not None:
            break

    if player is None:
        return

    game["last_activity_at"] = time.time()

    if not game["game_started"] or game["game_over"]:
        return

    if not all(player["connected"] for player in game["players"]):
        return

    if game["players"][0]["sid"] == request.sid:
        current_player = "player1"
    else:
        current_player = "player2"

    if current_player != game["current_player"]:
        emit("memory_invalid_move", {"message": "It is not your turn"})
        return

    if not isinstance(position, int) or position < 0 or position >= 16:
        return

    if position in game["matched"] or position in game["revealed"]:
        return

    if game["resolving_turn"] or len(game["flipped_cards"]) >= 2:
        return

    game["flipped_cards"].append(position)
    game["revealed"].append(position)

    visible_board = []

    for i in range(len(game["board"])):
        if i in game["matched"] or i in game["revealed"]:
            visible_board.append(game["board"][i])
        else:
            visible_board.append(None)

    socketio.emit("memory_board_updated", {"board": visible_board,"matched": game["matched"],
                                            "revealed": game["revealed"],
                                            "current_player": game["current_player"],
                                            "scores": game["scores"]}, to=room)

    if len(game["flipped_cards"]) == 2:

        first = game["flipped_cards"][0]
        second = game["flipped_cards"][1]

        if game["board"][first] == game["board"][second]:

            game["matched"].append(first)
            game["matched"].append(second)

            game["scores"][current_player] += 1

            remaining = []

            game["flipped_cards"] = []

            for position in game["revealed"]:
                if position not in game["matched"]:
                    remaining.append(position)

            game["revealed"] = remaining

            send_board_update(room, game)

            if len(game["matched"]) == 16:
                game["game_over"] = True

                if game["scores"]["player1"] > game["scores"]["player2"]:
                    result = "player1"
                elif game["scores"]["player2"] > game["scores"]["player1"]:
                    result = "player2"
                else:
                    result = "draw"

                socketio.emit("memory_game_over", {"winner": result,"scores": game["scores"]}, to=room)

            else:
                socketio.emit("memory_pair_matched", {"matched": game["matched"],"scores": game["scores"],
                    "current_player": game["current_player"]
                }, to=room)

        else:
            game["resolving_turn"] = True
            socketio.start_background_task(hide_mismatched_cards, room, first, second, current_player, game["version"])

@socketio.on("memory_request_rematch")
def request_rematch(data):

    room = data["room"]

    if room not in memory_games:
        return

    game = memory_games[room]

    if not game["game_started"]:
        return

    if game["rematch_request"] is not None and game["rematch_request"] != session["user_id"]:
        return

    game["rematch_request"] = session["user_id"]

    emit("memory_rematch_requested", {"message": "Opponent wants to play again"},
         to=room, include_self=False)

@socketio.on("memory_rematch_response")
def rematch_response(data):

    room = data["room"]
    response = data["response"]

    if room not in memory_games:
        return

    game = memory_games[room]

    if game["rematch_request"] is None:
        return

    if response == "decline":
        game["rematch_request"] = None
        game["version"] += 1
        emit("memory_rematch_declined", {"message": "Rematch declined"}, to=room)
        return

    if response == "accept":

        if game["rematch_request"] == session["user_id"]:
            return

        game["board"] = new_board()
        game["matched"] = []
        game["revealed"] = []
        game["flipped_cards"] = []
        game["resolving_turn"] = False
        game["scores"] = {"player1": 0, "player2": 0}
        game["game_over"] = False
        game["rematch_request"] = None

        game["starter"] = "player2" if game["starter"] == "player1" else "player1"
        game["current_player"] = game["starter"]

        emit("memory_rematch_accepted", {"board": build_visible_board(game),
                                         "matched": game["matched"],
                                         "revealed": game["revealed"],
                                         "current_player": game["current_player"],
                                         "scores": game["scores"]}, to=room)



