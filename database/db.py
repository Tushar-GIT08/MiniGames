import sqlite3

DB_PATH = "database/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game TEXT NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ttt_games(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        board TEXT NOT NULL,
        player_symbol TEXT NOT NULL,
        computer_symbol TEXT NOT NULL,
        turn TEXT NOT NULL,
        game_over INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id))
    """)

    conn.commit()
    conn.close()

def find_user(username,email):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",(username, email)
    )

    user = cursor.fetchone()
    conn.close()

    return user

def create_user(username, email, password):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(username, email, password) VALUES(?, ?, ?)",
        (username, email, password)
    )

    conn.commit()
    conn.close()

def get_game_record(user_id , game):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wins, losses, draws
        FROM game_records
        WHERE user_id = ? and game = ?
        """,
        (user_id, game)
    )

    record = cursor.fetchone()
    conn.close()

    return record

def create_record(user_id , game):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO game_records
        (user_id, game, wins, losses, draws)
        VALUES(?, ?, 0, 0, 0)
        """,
        (user_id, game)
    )

    conn.commit()
    conn.close()

def update_record(user_id, game, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if result == "win":

        cursor.execute("""
        UPDATE game_records
        SET wins = wins + 1
        WHERE user_id = ? and game = ?
        """,
        (user_id, game)
    )

    elif result == "loss":
        cursor.execute("""
        UPDATE game_records
        SET losses = losses + 1
        WHERE user_id = ? and game = ?
        """,
        (user_id, game)
    )

    else:
        cursor.execute("""
        UPDATE game_records
        SET draws = draws + 1
        WHERE user_id = ? and game = ?
        """,
        (user_id, game)
    )
    
    conn.commit()
    conn.close()

def get_ttt_game(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT board, player_symbol, computer_symbol, turn, game_over
        FROM ttt_games
        WHERE user_id = ?
        """,
        (user_id,)
    )
    game = cursor.fetchone()

    conn.close()

    return game

def create_ttt_game(user_id, board, player_symbol, computer_symbol, turn):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ttt_games
        (user_id, board, player_symbol, computer_symbol, turn, game_over)
        VALUES(?, ?, ?, ?, ?, 0)
        """,
        (user_id, board, player_symbol, computer_symbol, turn)
    )

    conn.commit()
    conn.close()

def update_ttt_game(user_id, board, turn, game_over):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE ttt_games
        SET board = ? , turn = ? , game_over = ?
        WHERE user_id = ?
        """,
        (board, turn, game_over, user_id)
    )

    conn.commit()
    conn.close()

def delete_ttt_game(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM ttt_games WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

def get_username(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username FROM users WHERE id = ?",
        (user_id,)
    )

    username = cursor.fetchone()

    conn.close()

    return username[0]
    

