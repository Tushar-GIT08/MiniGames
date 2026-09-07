from flask import Blueprint, render_template, session, redirect , request , jsonify
import random

from database.db import(
    create_ttt_game,
    get_ttt_game,
    update_ttt_game,
    delete_ttt_game,
    get_game_record,
    create_record,
    update_record,
    get_username
)

tictactoe = Blueprint("tictactoe", __name__)

def check_winner(board , symbol):

    winning_patterns = [

        [0,1,2], #HORIZONTAL PATTERN...
        [3,4,5],
        [6,7,8],

        [0,3,6], #VERTICAL PATTERN...
        [1,4,7],
        [2,5,8],

        [0,4,8], #DIAGONAL PATTERN...
        [6,4,2]
    ]

    for i in winning_patterns:

        if ( board[i[0]] == symbol and board[i[1]] == symbol and board[i[2]] == symbol):
            return True
       
    return False


@tictactoe.route("/tictactoe" , methods=["GET" , "POST"])
def tictactoe_game():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    username = get_username(user_id)

    record = get_game_record(user_id, "tictactoe")

    if record is None:
        create_record(user_id, "tictactoe")
        record = get_game_record(user_id, "tictactoe")

    game = get_ttt_game(user_id)

    if game is None:

        board = "_________"

        if random.choice(["X", "O"]) == "X":
            player_symbol = "X"
            computer_symbol = "O"
            turn = "player"
        else:
            player_symbol = "O"
            computer_symbol = "X"
            turn = "computer"

        create_ttt_game(user_id, board, player_symbol, computer_symbol, turn)

        game = get_ttt_game(user_id)

        if turn == "computer":

            computer_position = random.choice(range(9))

            board = (
                board[:computer_position] + computer_symbol + board[computer_position + 1:]
            )

            update_ttt_game(user_id,board,"player",0)

            game = get_ttt_game(user_id)


    if request.method == "POST":

        data = request.get_json()

        position = int(data["position"])

        board = game[0]

        if board[position] == "_" and game[3] == "player":

            board = board[:position] + game[1] + board[position + 1:]

            if check_winner(board, game[1]):

                update_ttt_game(user_id,board,"player",1)

                update_record(user_id, "tictactoe", "win")

                return jsonify({"board": board,"winner": "player"})

            empty_positions = []

            for i in range(9):
                if board[i] == '_':
                    empty_positions.append(i)

            if len(empty_positions) > 0:
                computer_position = random.choice(empty_positions)

                board = (board[:computer_position]+ game[2] + board[computer_position + 1:])

                if check_winner(board, game[2]):

                    update_ttt_game(
                        user_id,
                        board,
                        "player",
                        1
                    )

                    update_record(user_id, "tictactoe", "loss")


                    return jsonify({
                        "board": board,
                        "winner": "computer"
                    })


                if "_" not in board:
                    update_ttt_game(user_id, board, "player", 1)

                    update_record(user_id, "tictactoe", "draw")

                    return jsonify({
                        "board" : board,
                        "winner" : "draw"
                    })

            update_ttt_game(user_id,board,"player",0)

            return jsonify({"board" : board})

        return jsonify({"board" : board})

    return render_template(
        "tictactoe.html",
        game=game,
        record=record,
        username=username
    )

@tictactoe.route("/tictactoe/reset")
def reset_tictactoe():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    delete_ttt_game(user_id)

    return redirect("/tictactoe")

