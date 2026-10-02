const tiles = [
    "🤓", "💩", "🥸", "🥵",
    "😂", "😭", "😈", "🤬",
    "🤓", "💩", "🥸", "🥵",
    "😂", "😭", "😈", "🤬"
]; 

let card1 = null;
let card2 = null;

let lock = false;

let moves = 0;

let match = 0;

let startTime = null;
let timerCurrent = null;
let elapsed = null;
let minutes = 0;
let seconds = 0;
let formattedSeconds = 0;
let time = "0:00";


for (let i = tiles.length - 1; i >= 0; i--) { 
    let j = Math.floor(Math.random() * (i + 1));
    
    [tiles[i], tiles[j]] = [tiles[j], tiles[i]];

}

const box = document.querySelector(".box");
const movesNumber = document.getElementById("moves");
const result = document.getElementById("result");
const timer = document.getElementById("timer");


for (let i = 0; i < tiles.length; i++) {

    const card = document.createElement("button");
    
    card.dataset.value = tiles[i];

    card.textContent = "?";

    card.addEventListener("click", function() {

        if (lock) {
            return;
        }

        if (card1 === null) {

            card1 = card; 
            card.textContent = card.dataset.value;

            if (startTime === null) {
                
                startTime = Date.now();
                timerCurrent = setInterval(function() {

                    elapsed = Math.floor((Date.now() - startTime) / 1000);
                    minutes = Math.floor(elapsed / 60);
                    seconds = elapsed % 60;

                    formattedSeconds = seconds < 10 ? "0" + seconds : seconds;

                    timer.textContent = "Time: " + minutes + ":" + formattedSeconds;

                    time = minutes + ":" + formattedSeconds;

                }, 1000);
            }

        }


        else if (card2 === null) {

            if (card === card1) {
                return;
            }
            
            card2 = card;
            card.textContent = card.dataset.value;

            moves++;
            movesNumber.textContent = "Moves: " + moves;

            console.log(moves);

            lock = true;

            if (card1.dataset.value === card2.dataset.value) {
                card1.disabled = true;
                card2.disabled = true;

                match++;

                if (match === 8) {
                    lock = true;
                    result.textContent = "YOU COMPLETED THE GAME";

                    fetch("/memory", { method: "POST",headers: {"Content-Type": "application/json"},

                        body: JSON.stringify({moves: moves, time: time, result: "completed"})
                    });

                    clearInterval(timerCurrent);

                }else {

                    lock = false;

                }

                card1 = null;
                card2 = null;
            
            }else {
                setTimeout(function() {
                    card1.textContent = "?";
                    card2.textContent = "?";

                    card1 = null;
                    card2 = null;

                    lock = false;

                }, 1000);
            }
        }
    });
    box.appendChild(card);
}

const reset = document.getElementById("reset");
reset.addEventListener("click", function() {

    window.location.href = "/memory/reset";

});

const prev_button = document.getElementById("prev");
const prev_popup = document.getElementById("prev_popup");
const btg = document.getElementById("btg")

prev_button.addEventListener("click", function() {

    prev_popup.style.display = "flex";

});

btg.addEventListener("click", function() {

    prev_popup.style.display = "none";

});