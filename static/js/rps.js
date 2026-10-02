const buttons = document.querySelectorAll(".rps-choice");

const images = {
    rock: "/static/images/rock-emoji.png",
    paper: "/static/images/paper-emoji.png",
    scissors: "/static/images/scissors-emoji.png"
};


buttons.forEach(function(button){

    button.addEventListener("click", function(){

        const choice = button.dataset.choice;

            fetch("/rps/1p", {method: "POST",headers: {"Content-Type": "application/json"},
            
            body: JSON.stringify({choice: choice})
        
        })
        
        .then(response => response.json())
        .then(data => {

            document.getElementById("player-image").src = images[data.choice];

            document.getElementById("comp-image").src = images[data.comp_choice];

            document.getElementById("result").textContent = data.result;

            const scores = document.querySelectorAll(".results-box p");

            scores[1].textContent = "Wins: " + data.wins;
            scores[2].textContent = "Losses: " + data.losses;
            scores[3].textContent = "Draws: " + data.draws;
        });
    });
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



