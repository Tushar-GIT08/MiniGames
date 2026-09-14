const socket = io();

const createRoom = document.getElementById("create-room")
const roomCode = document.getElementById("room-code");
const joinButton = document.getElementById("join");
const showJoinButton = document.getElementById("show-join-room");
const roomMessage = document.getElementById("room-message");
const joinSection = document.getElementById("join-section");

const waiting = document.getElementById("waiting");
const board = document.querySelector(".board");
const roomMenu = document.getElementById("room-menu");


let mySymbol = null;
let room = null;

const tttButtons = document.querySelectorAll(".board button");

tttButtons.forEach(function(button) {
    button.addEventListener("click", function() {

        const position = button.dataset.position;
        socket.emit("make_move", {room: room,position: Number(position)});
    
    });
});

createRoom.addEventListener("click", function() {

    socket.emit("create_room");

});

showJoinButton.addEventListener("click", function() {

    joinSection.style.display = "block";
});

joinButton.addEventListener("click", function() {
    
    room = roomCode.value;
    socket.emit("join_game", {room: room});
});

socket.on("room_created", function(data) {
    room = data.room;
    mySymbol = data.symbol;

    document.getElementById("waiting-room-code").textContent = "Room Code: " + room;

    document.getElementById("my-symbol").textContent = "You = " + mySymbol;
    
    if (mySymbol === "X") {
        document.getElementById("opponent-symbol").textContent = "Opponent = O";
    }
    else {
        document.getElementById("opponent-symbol").textContent = "Opponent = X";
    }

    roomMenu.style.display = "none";
    waiting.style.display = "block";
});

socket.on("room_not_found", function(data) {

    document.getElementById("room-message").textContent = data.message;
});

socket.on("room_full", function(data) {
    roomMessage.textContent = data.message;
});

socket.on("player_assigned", function(data) {
    mySymbol = data.symbol;

    document.getElementById("my-symbol").textContent ="You = " + mySymbol;
    
    if (mySymbol === "X") {
        document.getElementById("opponent-symbol").textContent ="Opponent = O";
    }
    else {
        document.getElementById("opponent-symbol").textContent ="Opponent = X";
    }

    roomMenu.style.display = "none";
    waiting.style.display = "block";
});

socket.on("game_started", function(data){

    waiting.style.display = "none";
    document.getElementById("game-info").style.display = "block";
    board.style.display = "grid";

    document.getElementById("game-controls").style.display = "block";
    document.getElementById("results").style.display = "block";
    document.getElementById("new-game").style.display = "block";
});

socket.on("board_update", function(data) {

    for (let i = 0; i < 9; i++) {
        tttButtons[i].textContent = data.board[i];
    }
});

socket.on("game_over", function(data) {

    for (let i = 0; i < 9; i++) {
        tttButtons[i].textContent = data.board[i];
        tttButtons[i].disabled = true;
    }

    const message = document.getElementById("message");

    if (data.winner === mySymbol) {
        message.textContent = "YOU WIN";
    }
    else if (data.winner === "draw") {
        message.textContent = "IT'S A DRAW";
    }
    else {
        message.textContent = "YOU LOSE";
    }
});

const newGame = document.getElementById("new-game");
    newGame.addEventListener("click", function() {
        socket.emit("request_rematch",{room : room})
});

const rematchPopup = document.getElementById("rematch-popup");
const acceptRematch = document.getElementById("accept-rematch");
const declineRematch = document.getElementById("decline-rematch");

socket.on("rematch_requested", function(data) {

    rematchPopup.style.display = "flex";
    
});
 
acceptRematch.addEventListener("click", function() {

    socket.emit("rematch_response", {room: room,response: "accept"});
    rematchPopup.style.display = "none";

});

declineRematch.addEventListener("click", function() {

    socket.emit("rematch_response", {room: room,response: "decline"});
    rematchPopup.style.display = "none";

});

socket.on("rematch_accepted", function(data) {

    mySymbol = data.symbol;

    document.getElementById("my-symbol").textContent = "You = " + mySymbol;

    if (mySymbol === "X") {
        document.getElementById("opponent-symbol").textContent = "Opponent = O";
    }
    else {
        document.getElementById("opponent-symbol").textContent = "Opponent = X";
    }

    for (let i = 0; i < 9; i++) {
        tttButtons[i].textContent = "_";
        tttButtons[i].disabled = false;
    }

    document.getElementById("message").textContent = "";
});

socket.on("rematch_declined", function(data) {
});

socket.on("opponent_disconnected", function(data) {

    document.getElementById("message").textContent ="OPPONENT DISCONNECTED";

    for (let i = 0; i < 9; i++) {
        tttButtons[i].disabled = true;
}

});

const resultsButton = document.getElementById("results");
const resultsPopup = document.getElementById("results-popup");
const backToGame = document.getElementById("btg");
const resultElements = document.querySelectorAll(".result");


resultsButton.addEventListener("click", function() {

    fetch("/tictactoe/results").then(function(response) {
            return response.json();
    })
        
    .then(function(data) {

        resultElements[0].textContent = "Wins: " + data.wins;
        resultElements[1].textContent = "Losses: " + data.losses;
        resultElements[2].textContent = "Draws: " + data.draws;

        resultsPopup.style.display = "flex";
    });
});


backToGame.addEventListener("click", function() {
    resultsPopup.style.display = "none";
});
