const form = document.getElementById("guess-form");

form.addEventListener("submit", function(event) {

    event.preventDefault();

    const guess = document.getElementById("guess").value.toLowerCase();

    if(!/^[a-zA-Z]$/.test(guess)) {

        document.getElementById("message").textContent = "Wrong input.Enter only letters"

        document.getElementById("guess").value = "";

        return;

    }

    fetch("/hangman", {

        method: "POST",

        headers: {"Content-Type": "application/json"},

        body: JSON.stringify({guess: guess})

    })

    .then(response => response.json())

    .then(data => {

        console.log(data);

        document.getElementById("word").textContent = data.hidden_word;

        document.getElementById("hangman-image").src = 
        "/static/images/hangman" + data.wrong_guesses + ".svg";

        if (data.game_over) {
            
            document.getElementById("guess").disabled = true;
            document.querySelector("#guess-form button").disabled = true;


            if (data.wrong_guesses >= 5) {

                document.getElementById("message").textContent ="YOU LOST! The word was " + data.word.toUpperCase();
            }

            else {
                document.getElementById("message").textContent ="YOU WON!";
            }

        }

    });

});

const newGame = document.getElementById("new-game")
newGame.addEventListener("click" , function(){

    fetch('/reset')
    
    .then(response => response.text())

    .then(data => {
        
        console.log(data);

        location.reload();
    
    });
});

