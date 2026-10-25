const socket = io();

const roomMenu = document.getElementById("room-menu");
const joinSection = document.getElementById("join-section");
const roomCode = document.getElementById("room-code");
const roomMessage = document.getElementById("room-message");
const waiting = document.getElementById("waiting");
const waitingCode = document.getElementById("waiting-room-code");
const gameArea = document.getElementById("memory-game");

const cards = document.querySelectorAll(".box button");
const board = document.querySelector(".box");
const scoreText = document.getElementById("memory-score");
const turnText = document.getElementById("memory-turn");
const memoryMessage = document.getElementById("memory-message");

const rejoin = document.getElementById("rejoin");
const rejoinButton = document.getElementById("rejoin-game");
const previousRoom = document.getElementById("previous-room");

const newGameButton = document.getElementById("new-game");
const rematchPopup = document.getElementById("rematch-popup");

let myRole = null;   
let room = null;
let autoRejoin = false;
let currentTurn = null;
let gameOver = false;

function drawBoard(data) {
    for (let i = 0; i < 16; i++) {
        cards[i].textContent = data.board[i] || "";
        cards[i].classList.toggle("matched", data.matched.includes(i));
    }
}

function showScore(scores) {
    const mine = (myRole === "player1") ? scores.player1 : scores.player2;
    const theirs = (myRole === "player1") ? scores.player2 : scores.player1;

    scoreText.textContent = "You " + mine + " - " + theirs + " Opponent";
}

function showTurn(currentPlayer) {
    currentTurn = currentPlayer;
    const myTurn = (currentPlayer === myRole);
    turnText.textContent = myTurn ? "YOUR TURN" : "OPPONENT'S TURN";
    board.classList.toggle("dimmed", !myTurn);
}

function renderState(data) {
    memoryMessage.textContent = "";
    drawBoard(data);
    showScore(data.scores);
    showTurn(data.current_player);
}

function showGameOver(scores) {
    const mine = (myRole === "player1") ? scores.player1 : scores.player2;
    const theirs = (myRole === "player1") ? scores.player2 : scores.player1;

    gameOver = true;

    if (mine > theirs) {
        turnText.textContent = "YOU WIN";
    } else if (mine < theirs) {
        turnText.textContent = "YOU LOSE";
    } else {
        turnText.textContent = "IT'S A DRAW";
    }

    board.classList.add("dimmed");
}

document.getElementById("create-room").addEventListener("click", function () {
    socket.emit("memory_create_room");
});

document.getElementById("show-join-room").addEventListener("click", function () {
    joinSection.style.display = "block";
});

document.getElementById("join").addEventListener("click", function () {
    roomMessage.textContent = "";
    room = roomCode.value;
    socket.emit("memory_join_game", { room: room });
});

socket.on("memory_room_created", function (data) {
    room = data.room;
    roomMenu.style.display = "none";
    waitingCode.textContent = data.room;
    waiting.style.display = "block";
});

socket.on("memory_room_full", function (data) {
    roomMessage.textContent = data.message;
});

socket.on("memory_already_joined", function (data) {
    roomMessage.textContent = data.message;
});

socket.on("memory_room_not_found", function (data) {
    localStorage.removeItem("memoryRoom");
    rejoin.style.display = "none";

    if (autoRejoin) {
        autoRejoin = false;
        return;
    }

    roomMessage.textContent = data.message;
});

socket.on("memory_expired", function (data) {
    localStorage.removeItem("memoryRoom");
    rejoin.style.display = "none";

    if (autoRejoin) {
        autoRejoin = false;
        return;
    }

    roomMessage.textContent = data.message;
});

socket.on("memory_game_over", function (data) {
    showScore(data.scores);
    showGameOver(data.scores);
});

socket.on("memory_valid_reconnect", function (data) {
    autoRejoin = false;
    myRole = data.player;

    roomMenu.style.display = "none";
    waiting.style.display = "none";
    gameArea.style.display = "block";

    renderState(data);

    if(data.game_over) {
        showGameOver(data.scores);
    }

    if(data.rematch_pending) {
        rematchPopup.style.display = "flex";
    }

});

socket.on("opponent_disconnected", function (data) {
    memoryMessage.textContent = data.message;
    board.classList.add("dimmed");
});

socket.on("memory_opponent_reconnected", function (data) {
    memoryMessage.textContent = data.message;
    
    if(!gameOver) {
        showTurn(currentTurn);
    }
});

socket.on("memory_game_started", function (data) {
    myRole = data.player;
    roomMenu.style.display = "none";
    waiting.style.display = "none";
    gameArea.style.display = "block";
    renderState(data);
    localStorage.setItem("memoryRoom", room);
});

socket.on("memory_board_updated", function (data) {
    renderState(data);
});

socket.on("memory_invalid_move", function (data) {
    memoryMessage.textContent = data.message;
});

cards.forEach(function (card) {
    card.addEventListener("click", function () {
        socket.emit("memory_flip_card", { position: Number(card.dataset.position) });
    });
});

socket.on("memory_rematch_requested", function () {
    rematchPopup.style.display = "flex";
});

socket.on("memory_rematch_accepted", function (data) {
    gameOver = false;
    rematchPopup.style.display = "none";
    renderState(data);
});

socket.on("memory_rematch_declined", function (data) {
    memoryMessage.textContent = data.message;
});

const savedRoom = localStorage.getItem("memoryRoom");
const navEntry = performance.getEntriesByType("navigation")[0];
const isReload = navEntry && navEntry.type === "reload";

if (savedRoom) {
    if (isReload) {
        autoRejoin = true;
        room = savedRoom;
        socket.emit("memory_join_game", { room: savedRoom });
    } else {
        rejoin.style.display = "block";
        previousRoom.textContent = "Previous Room: " + savedRoom;
    }
}

rejoinButton.addEventListener("click", function () {
    roomMessage.textContent = "";
    room = savedRoom;
    socket.emit("memory_join_game", { room: savedRoom });
});

document.querySelector(".home-button").addEventListener("click", function () {
    localStorage.removeItem("memoryRoom");
});

newGameButton.addEventListener("click", function () {
    socket.emit("memory_request_rematch", { room: room });
    memoryMessage.textContent = "REMATCH REQUESTED...";
});

document.getElementById("accept-rematch").addEventListener("click", function () {
    socket.emit("memory_rematch_response", { room: room, response: "accept" });
    rematchPopup.style.display = "none";
});

document.getElementById("decline-rematch").addEventListener("click", function () {
    socket.emit("memory_rematch_response", { room: room, response: "decline" });
    rematchPopup.style.display = "none";
});

