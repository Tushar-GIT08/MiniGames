const tiles = ["A","B","C","D","E","F","G","H","A","B","C","D","E","F","G","H"]; 

let card1 = null;
let card2 = null;

let lock = false;

let moves = 0;

for (let i = tiles.length-1; i >= 0; i--) {
    let j = Math.floor(Math.random() * (i + 1));
    
    [tiles[i] , tiles[j]] = [tiles[j] , tiles[i]]

}

const box = document.querySelector(".box");
const movesNumber = document.getElementById("moves")

for(let i = 0; i < tiles.length; i++ ){

    const card = document.createElement("button")
    
    card.dataset.value = tiles[i]

    card.textContent = "?"

    card.addEventListener("click", function(){

        if(lock){
            return;
        }

        if(card1 === null){
            card1 = card; 
            card.textContent = card.dataset.value;
        }

        else if(card2 === null){

            if(card === card1){
                return
            }
            
            card2 = card;
            card.textContent = card.dataset.value;

            moves++;
            movesNumber.textContent = "Moves: " + moves;

            console.log(moves)

            lock = true;

            if(card1.dataset.value === card2.dataset.value){
                card1.disabled = true;
                card2.disabled = true;

                card1 = null;
                card2 = null;

                lock = false;

            }else{
                setTimeout(function(){
                    card1.textContent = "?";
                    card2.textContent = "?";

                    card1 = null;
                    card2 = null;

                    lock = false;

                }, 1000);
            }


            }
        })
        box.appendChild(card);


    }


