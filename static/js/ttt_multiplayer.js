const socket = io();

const createRoom = document.getElementById("create-room");
const roomCode = document.getElementById("room-code");
const joinButton = document.getElementById("join");
const showJoinButton = document.getElementById("show-join-room");
const roomMessage = document.getElementById("room-message");
const joinSection = document.getElementById("join-section");

const waiting = document.getElementById("waiting");
const board = document.querySelector(".board");
const roomMenu = document.getElementById("room-menu");

const rejoin = document.getElementById("rejoin");
const rejoinButton = document.getElementById("rejoin-game");
const previousRoom = document.getElementById("previous-room");

const message = document.getElementById("message");
const mySymbolText = document.getElementById("my-symbol");
const opponentSymbolText = document.getElementById("opponent-symbol");
const tttButtons = document.querySelectorAll(".board button");



let mySymbol = null;
let room = null;
const savedRoom = localStorage.getItem("tttRoom");

if (savedRoom) {
    
    rejoin.style.display = "block";
    
    previousRoom.textContent = "Previous Room: " + savedRoom;
}

function showSymbols() {
    mySymbolText.textContent = "You = " + mySymbol;
    opponentSymbolText.textContent = "Opponent = " + (mySymbol === "X" ? "O" : "X");
}

function showTurn(turn) {
    const myTurn = (turn === mySymbol);
    message.textContent = myTurn ? "YOUR TURN" : "OPPONENT'S TURN";
    board.classList.toggle("dimmed", !myTurn);
}

function showGameScreen() {
    waiting.style.display = "none";
    roomMenu.style.display = "none";
    document.getElementById("game-info").style.display = "block";
    board.style.display = "grid";
    document.getElementById("game-controls").style.display = "block";
    document.getElementById("results").style.display = "block";
    document.getElementById("new-game").style.display = "block";
}

function drawBoard(boardString) {
    for (let i = 0; i < 9; i++) {
        tttButtons[i].textContent = boardString[i];
    }
}

tttButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        socket.emit("ttt_make_move", { room: room, position: Number(button.dataset.position) });
    });
});

createRoom.addEventListener("click", function () {
    socket.emit("ttt_create_room");
});

showJoinButton.addEventListener("click", function () {
    joinSection.style.display = "block";
});

joinButton.addEventListener("click", function () {
    roomMessage.textContent = "";
    room = roomCode.value;
    socket.emit("ttt_join_game", { room: room });
});

rejoinButton.addEventListener("click", function () {
    room = savedRoom;
    socket.emit("ttt_join_game", { room: room });
});

// SOCKET EVENTS

socket.on("room_created", function (data) {
    room = data.room;
    localStorage.setItem("tttRoom", room);
    mySymbol = data.symbol;

    document.getElementById("waiting-room-code").textContent = room;
    showSymbols();

    roomMenu.style.display = "none";
    waiting.style.display = "block";
});

socket.on("room_not_found", function (data) {
    roomMessage.textContent = data.message;
    localStorage.removeItem("tttRoom");
    rejoin.style.display = "none";
});

socket.on("room_full", function (data) {
    roomMessage.textContent = data.message;
});

socket.on("player_assigned", function (data) {
    localStorage.setItem("tttRoom", room);
    mySymbol = data.symbol;
    showSymbols();

    roomMenu.style.display = "none";
    waiting.style.display = "block";
});

socket.on("game_started", function (data) {
    showGameScreen();
    showTurn(data.turn);
});

socket.on("board_update", function (data) {
    drawBoard(data.board);
    showTurn(data.turn);
});

socket.on("game_state", function (data) {
    rejoin.style.display = "none";
    mySymbol = data.symbol;
    showSymbols();
    drawBoard(data.board);
    showGameScreen();

    if (data.game_over) {
        tttButtons.forEach(function (b) { b.disabled = true; });
        board.classList.add("dimmed");
    } else {
        showTurn(data.turn);
    }
});

socket.on("game_over", function (data) {
    drawBoard(data.board);
    board.classList.add("dimmed");
    tttButtons.forEach(function (b) { b.disabled = true; });
    

    if (data.winner === mySymbol) {
        message.textContent = "YOU WIN";
    } else if (data.winner === "draw") {
        message.textContent = "IT'S A DRAW";
    } else {
        message.textContent = "YOU LOSE";
    }
});

const rematchPopup = document.getElementById("rematch-popup");

document.getElementById("new-game").addEventListener("click", function () {
    socket.emit("ttt_request_rematch", { room: room });
    message.textContent = "REMATCH REQUESTED...";
});

socket.on("rematch_requested", function () {
    rematchPopup.style.display = "flex";
});

document.getElementById("accept-rematch").addEventListener("click", function () {
    socket.emit("ttt_rematch_response", { room: room, response: "accept" });
    rematchPopup.style.display = "none";
});

document.getElementById("decline-rematch").addEventListener("click", function () {
    socket.emit("ttt_rematch_response", { room: room, response: "decline" });
    rematchPopup.style.display = "none";
});

socket.on("rematch_accepted", function (data) {
    mySymbol = data.symbol;
    showSymbols();

    tttButtons.forEach(function (b) {
        b.textContent = "_";
        b.disabled = false;
    });

    showTurn(data.turn);
});

socket.on("rematch_declined", function (data) {
    message.textContent = data.message;
});

socket.on("opponent_disconnected", function (data) {
    message.textContent = "OPPONENT DISCONNECTED";
    board.classList.add("dimmed");
    tttButtons.forEach(function (b) { b.disabled = true; });
});

socket.on("opponent_reconnected", function () {
    message.textContent = "OPPONENT RECONNECTED";
    board.classList.remove("dimmed");
    tttButtons.forEach(function (b) { b.disabled = false; });
});

socket.on("rejoin_expired", function (data) {
    roomMessage.textContent = data.message;
    localStorage.removeItem("tttRoom");
    rejoin.style.display = "none";
});

//LIFETIME RESULTS
const resultsButton = document.getElementById("results");
const resultsPopup = document.getElementById("results-popup");
const resultElements = document.querySelectorAll(".result");

resultsButton.addEventListener("click", function () {
    fetch("/tictactoe/results")
        .then(function (response) { return response.json(); })
        .then(function (data) {
            resultElements[0].textContent = "Wins: " + data.wins;
            resultElements[1].textContent = "Losses: " + data.losses;
            resultElements[2].textContent = "Draws: " + data.draws;
            resultsPopup.style.display = "flex";
        });
});

document.getElementById("btg").addEventListener("click", function () {
    resultsPopup.style.display = "none";
});