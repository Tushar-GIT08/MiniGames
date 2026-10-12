from flask import request
from flask_socketio import SocketIO
import time 
import random
import string

socketio = SocketIO()

all_rooms = []

DISCONNECT_NOTICE = 7
REJOIN_GRACE_SECONDS = 120   
ROOM_TTL_SECONDS = 1800       

def register_rooms(rooms):
    all_rooms.append(rooms)

def generate_room_code():
    while True:
        code = "".join(random.choice(string.digits) for _ in range(4))

        if not any(code in rooms for rooms in all_rooms):
            return code

def notify(room, player, disconnected_at):
    socketio.sleep(DISCONNECT_NOTICE)

    if not player["connected"] and player["disconnected_at"] == disconnected_at:
        player["notified"] = True
        socketio.emit("opponent_disconnected", {"message": "Opponent disconnected"}, to=room)


@socketio.on("disconnect")
def handle_disconnect():

    for rooms in all_rooms:
        for room in rooms:
            for player in rooms[room]["players"]:

                if player["sid"] == request.sid:

                    player["sid"] = None
                    player["connected"] = False
                    player["disconnected_at"] = time.time()
                    player["notified"] = False

                    socketio.start_background_task(notify, room, player, player["disconnected_at"])
                    return