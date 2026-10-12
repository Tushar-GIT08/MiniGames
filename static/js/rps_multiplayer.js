const socket = io();

const roomMenu = document.getElementById("room-menu");
const joinSection = document.getElementById("join-section");
const roomCode = document.getElementById("room-code");
const roomMessage = document.getElementById("room-message");
const waiting = document.getElementById("waiting");
const waitingCode = document.getElementById("waiting-room-code");
const gameArea = document.getElementById("rps-game");
const rpsResult = document.getElementById("rps-result");
const rejoin = document.getElementById("rejoin");
const rejoinButton = document.getElementById("rejoin-game");
const previousRoom = document.getElementById("previous-room");
const scoreText = document.getElementById("score");

const images = {
    rock: "/static/images/rock-emoji.png",
    paper: "/static/images/paper-emoji.png",
    scissors: "/static/images/scissors-emoji.png"
};

const roundResult = document.getElementById("round-result");
const myChoiceImage = document.getElementById("my-choice-image");
const opponentChoiceImage = document.getElementById("opponent-choice-image");
const roundOutcome = document.getElementById("round-outcome");

let myRole = null;
let room = null;
let autoRejoin = false;

document.getElementById("create-room").addEventListener("click", function () {
    localStorage.removeItem("rpsRoom");
    
    rejoin.style.display = "none";
    socket.emit("rps_create_room");
});

document.getElementById("show-join-room").addEventListener("click", function () {
    joinSection.style.display = "block";
});

document.getElementById("join").addEventListener("click", function () {
    localStorage.removeItem("rpsRoom");
    rejoin.style.display = "none";
    
    roomMessage.textContent = "";
    room = roomCode.value;
    socket.emit("rps_join_game", { room: roomCode.value });

});

document.querySelectorAll(".rps-choice").forEach(function (button) {
    button.addEventListener("click", function () {
        socket.emit("rps_make_choice", { choice: button.dataset.choice });

        myChoiceImage.src = images[button.dataset.choice];
        opponentChoiceImage.src = "";
        roundOutcome.textContent = "";
        roundResult.style.display = "flex";


        rpsResult.textContent = "YOU CHOSE " + button.dataset.choice + " - WAITING FOR OPPONENT";

        document.querySelectorAll(".rps-choice").forEach(function (choiceButton){ 
            choiceButton.disabled = true;
        });
    });
});

socket.on("rps_room_created", function (data) {
    roomMenu.style.display = "none";
    waitingCode.textContent = data.room;
    waiting.style.display = "block";
    room = data.room;
});

socket.on("rps_game_started", function (data) {
    myRole = data.player;
    roomMenu.style.display = "none";
    waiting.style.display = "none";
    gameArea.style.display = "block";
    localStorage.setItem("rpsRoom", room);
});

function showScore(score) {
    const myScore = (myRole === "player1") ? score.player1 : score.player2;
    const theirScore = (myRole === "player1") ? score.player2 : score.player1;

    scoreText.textContent = "You " + myScore + " - " + theirScore + " Opponent";
}

function showRoundResult(data) {

    if (data.score) {
        showScore(data.score);
    }

    const iAmPlayer1 = (myRole === "player1");

    const myChoice = iAmPlayer1 ? data.player1_choice : data.player2_choice;
    const opponentChoice = iAmPlayer1 ? data.player2_choice : data.player1_choice;
    const myResult = iAmPlayer1 ? data.player1_result : data.player2_result;

    let resultMessage;

    if (myResult === "win") {
        resultMessage = "YOU WON!!";
    } else if (myResult === "loss") {
        resultMessage = "YOU LOST!!";
    } else {
        resultMessage = "IT'S A DRAW!!";
    }

    rpsResult.textContent = "";

    myChoiceImage.src = images[myChoice];
    opponentChoiceImage.src = images[opponentChoice];
    roundOutcome.textContent = resultMessage;
    roundResult.style.display = "flex";

    document.querySelectorAll(".rps-choice").forEach(function (choiceButton) {
        choiceButton.disabled = false;
    });
}

socket.on("rps_round_result", showRoundResult);

socket.on("rps_opponent_made_choice", function () {
    roundResult.style.display = "none";
    myChoiceImage.src = "";
    opponentChoiceImage.src = "";
    roundOutcome.textContent = "";
    
    rpsResult.textContent = "OPPONENT MADE THEIR MOVE - MAKE YOUR CHOICE";
    
});

socket.on("rps_room_not_found", function(data){
    localStorage.removeItem("rpsRoom");
    rejoin.style.display = "none";

    if(autoRejoin){
        autoRejoin = false;
        return;
    }
    
    roomMessage.textContent = data.message;
});

socket.on("rps_already_joined", function(data){
    roomMessage.textContent = data.message;
});

socket.on("rps_room_full", function(data){
    roomMessage.textContent = data.message;
});

socket.on("rps_opponent_reconnected", function (data) {
    rpsResult.textContent = data.message;

    document.querySelectorAll(".rps-choice").forEach(function (choiceButton) {
        choiceButton.disabled = false;
    });
});

socket.on("rps_valid_reconnect", function (data) {
    autoRejoin = false;
    myRole = data.player;
    showScore(data.score);

    roomMenu.style.display = "none";
    waiting.style.display = "none";
    gameArea.style.display = "block";

    if (data.my_choice) {
        myChoiceImage.src = images[data.my_choice];
        opponentChoiceImage.src = "";
        roundOutcome.textContent = "";
        roundResult.style.display = "flex";
        rpsResult.textContent = "YOU CHOSE " + data.my_choice + " - WAITING FOR OPPONENT";

        document.querySelectorAll(".rps-choice").forEach(function (choiceButton) {
            choiceButton.disabled = true;
        });

    } else if (data.opponent_chose) {
        rpsResult.textContent = "OPPONENT MADE THEIR MOVE - MAKE YOUR CHOICE";

    } else if (data.last_round) {
        showRoundResult(data.last_round);
    }
});

socket.on("rps_expired", function(data){
    localStorage.removeItem("rpsRoom");
    rejoin.style.display = "none";

    if(autoRejoin){
        autoRejoin = false;
        return;
    }

    roomMessage.textContent = data.message
});

socket.on("opponent_disconnected", function(data){
    rpsResult.textContent = data.message

    document.querySelectorAll(".rps-choice").forEach(function (choiceButton) {
        choiceButton.disabled = true;
    });
});

const savedRoom = localStorage.getItem("rpsRoom");

const navEntry = performance.getEntriesByType("navigation")[0];
const isReload = navEntry && navEntry.type === "reload";

if (savedRoom) {
    if (isReload) {
        autoRejoin = true;
        room = savedRoom;
        socket.emit("rps_join_game", { room: savedRoom });
    } else {
        rejoin.style.display = "block";
        previousRoom.textContent = "Previous Room: " + savedRoom;
    }
}

rejoinButton.addEventListener("click", function () {
    roomMessage.textContent = "";
    room = savedRoom;
    socket.emit("rps_join_game", { room: savedRoom });
});