"use strict";


const BASE_URL = "/api/sets";
let SET_ID;
let VERSES;

const $gameStartForm = $("#setCardsForm");
const $setCardsContainer = $("#setCardsContainer");
const $gameBoardContainer = $("#gameBoardContainer");
const $gameBoard = $("#gameBoard");


async function startGame(evt) {
  evt.preventDefault();
  $setCardsContainer.hide();

  SET_ID = $("#setId").val();

  await getNewVerses();
  
  makeCards();

  $gameBoardContainer.removeClass("d-none");
}

async function getNewVerses() {
  let resp = await axios.get(`${BASE_URL}/${SET_ID}`);
  VERSES = resp.data.cards;
}

/** Make up to 12 cards on the DOM with up to 6 verses */
function makeCards() {
  let cardsToMake = [];

  for(let i = 0; i < 6; i++) { 
    let verseObj = VERSES.pop();
    
    if(verseObj === undefined) break;

    let {reference, verse} = verseObj;
    cardsToMake.push({id: i, text: verse});
    cardsToMake.push({id: i, text: reference});
  };

  let $row = $("<div>").addClass("row");

  for(let j = 0; j < cardsToMake.length; j+=2) {
    let $col = $("<div>")
      .addClass(["col-lg-6", "my-2", "justify-contents-between", "mx-0"]);
    for(let k = j; k < j + 2; k++) {
      let cardData = cardsToMake[k];
      $col.append($(`
      <input type="checkbox" id="card-${k}" class="matchCard" data-id="${cardData.id}" />
      <label for="card-${k}" class="m-2">
      <div class="label-text">
      ${cardData.text}
      </div>
      </label>
      `));
    }
    $row.append($col);
  }
  $gameBoard.append($row);
}




$gameStartForm.on("submit", startGame);