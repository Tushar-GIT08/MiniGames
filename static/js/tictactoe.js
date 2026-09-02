const tttButtons = document.querySelectorAll(".board button");

console.log("Number of buttons:", tttButtons.length);

tttButtons.forEach(function(button) {

    button.addEventListener("click", function() {

        const position = button.dataset.position;

        console.log("Clicked position:", position);

        fetch("/tictactoe", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                position: position
            })

        })
        .then(response => {

            console.log("Response status:", response.status);

            return response.json();

        })
        .then(data => {

            console.log("Data from Flask:", data);

            const board = data.board;

            for (let i = 0; i < 9; i++) {

                tttButtons[i].textContent = board[i];

            }

            if (data.winner){

                const message = document.getElementById("message");

                if (data.winner === "player"){
                    message.textContent = "YOU WIN";
                }

                else if (data.winner === "computer"){
                    message.textContent = "COMPUTER WINS";
                }

                else if (data.winner === "draw"){
                    message.textContent = "IT'S A DRAW";
                }

                for(let i = 0; i<9; i++){
                    tttButtons[i].disabled = true;
                    
                }
            }

        });

    });

});

const newGame = document.getElementById("new-game");

newGame.addEventListener("click" , function(){

    window.location.href = "/tictactoe/reset";

});

const resultsButton = document.getElementById("results");
const resultsPopup = document.getElementById("results-popup");
const backToGame = document.getElementById("btg");

resultsButton.addEventListener("click", function() {

    resultsPopup.style.display = "flex";

});

backToGame.addEventListener("click", function() {

    resultsPopup.style.display = "none";

});