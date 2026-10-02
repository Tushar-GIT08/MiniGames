const socket = io();

const createRoom = document.getElementById("create-room");

createRoom.addEventListener("click", function(){
    socket.emit("rps_create_room");
});

const joinButton = document.getElementById("join");

joinButton.addEventListener("click", function(){
    const code = roomCode.value;

    socket.emit("rps_join_game", {room: code});
});

const showJoinButton = document.getElementById("show-join-room");

showJoinButton.addEventListener("click", function(){
    joinSection.style.display = "block"; 
});

const roomCode = document.getElementById("room-code");
const roomMessage = document.getElementById("room-message");
const joinSection = document.getElementById("join-section");








const buttons = document.querySelectorAll(".rps-choice");

buttons.forEach(function(button){
    button.addEventListener("click", function(){
        const choice = button.dataset.choice;

        socket.emit("rps_make_choice",{choice:choice});
    });
});




socket.on("rps_room_created", function(data){
    document.getElementById("room-message").textContent = "Room Code: " + data.room;
});

socket.on("rps_game_started", function(data){
    document.getElementById("room-menu").style.display = "none";
    document.getElementById("waiting").style.display = "none";
    document.getElementById("rps-game").style.display = "block";
});