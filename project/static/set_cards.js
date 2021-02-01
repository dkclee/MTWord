"use strict";

const BASE_URL = "/api/sets";
const SET_ID = $("#setId").val();;
const MAX_CARDS = 6;
const TOTAL_SECONDS = 30;
let verses = [];
let timerInterval;

const $gameStartForm = $("#setCardsForm");
const $cardsFormContainer = $("#cardsFormContainer");

const $gameBoardContainer = $("#gameBoardContainer");
const $gameBoard = $("#gameBoard");
const $gameFinishedModal = $("#gameFinishedModal");
const $playAgainBtn = $("#playAgainBtn");

/** Game controller
 *  - Called when the form is submitted to start the game
 *    only called once in the beginning
 */
async function startGameWithForm(evt) {
  evt.preventDefault();
  $cardsFormContainer.hide();
  
  await prepareGame();

  $gameBoardContainer.removeClass("d-none");
}

/** Game controller
 *  - Called when the user clicks the button to replay the game 
 *    on the modal
 */
async function startGameFromModal(evt) {
  $gameFinishedModal.modal("hide");
  await prepareGame();
}

$gameStartForm.on("submit", startGameWithForm);
$playAgainBtn.on("click", startGameFromModal);


/** Function that prepares the board and the game
 *  - Called by both functions with different ways 
 *    to start the game
 */
async function prepareGame() {
  $gameBoard.empty();

  if (verses.length === 0) await getNewVerses();

  $("#progressBar").css("width", `0%`);
  timerInterval = resetTimer(TOTAL_SECONDS);

  makeCards();
}

/** Main functionality of the game
 *  - if the two dataId's match, add a checked class to the label
 *    then disable the checking
 * 
 *  Check to see if the game has finished at the end
 */

function checkCards(evt) {
  let $checkedCards = $('input:checked');

  if ($checkedCards.length > 1) {
    let card1 = new GameCard($($checkedCards[0]));
    let card2 = new GameCard($($checkedCards[1]));

    // If the cards have the same id (verse and ref match)
    if (card1.dataId === card2.dataId) {
      card1.changeColor();
      card2.changeColor();

      card1.disableCheck();
      card2.disableCheck();
    }

    GameCard.uncheckCard($('input:checked'));
    GameCard.uncheckCard($(evt.target));

    let progressPercent = Math.floor(GameCard.getPercentageFlipped());
    $("#progressBar").css("width", `${progressPercent}%`);
  }

  if (GameCard.allCardsFlipped() === true) {
    clearInterval(timerInterval);
    $("#gameFinishedModalLabel").text("Congrats, You did it!");
    $gameFinishedModal.modal('show');
  }
}

$gameBoard.on("change", ".matchCard", checkCards);


/** Function to make the AJAX request when more cards are needed */
async function getNewVerses() {
  let resp = await axios.get(`${BASE_URL}/${SET_ID}`);
  verses = resp.data.cards;
  verses = _.shuffle(verses);
}

/** Make up to 12 cards on the DOM with up to 6 verses */
function makeCards() {
  let cardsToMake = [];

  for (let i = 0; i < MAX_CARDS; i++) {
    let verseObj = verses.pop();

    if (verseObj === undefined) break;

    let { reference, verse } = verseObj;
    cardsToMake.push({ dataId: i, text: verse });
    cardsToMake.push({ dataId: i, text: reference });
  };

  GameCard.numCards = cardsToMake.length;

  cardsToMake = _.shuffle(cardsToMake);

  for (let j = 0; j < cardsToMake.length; j++) {
    $gameBoard.append(GameCard.makeGameCard(cardsToMake[j], j));
  }
}


function resetTimer(seconds) {
  $("#timeLeft").text(seconds);
  let interval = setInterval(function () {
    seconds--;
    $("#timeLeft").text(seconds);
    if (seconds === 0) {

      clearInterval(interval);

      $gameFinishedModal.modal('show');
      $("#gameFinishedModalLabel")
        .text("Uh oh! It seems like you ran out of time 😢");
      
      $(".matchCard").attr("disabled", true);
    }
  }, 1000);

  return interval;
}
 
/** GameCard class to encapsulate all the data and functionality
 *  with changing and flipping cards
 */
class GameCard {
  static numCards;

  constructor($card) {
    this.dataId = $card.data("id");
    this.id = $card.attr('id').split("-")[1];
    this.$card = $card;
  }

  /** Add a CSS class to change card color */
  changeColor() {
    $(`#card-label-${this.id}`).addClass("checked");
  }

  /** Disable check so that the card cannot be selected again */
  disableCheck() {
    this.$card.attr("disabled", true);
  }

  /** Get ratio of flipped (with class checked) over total cards */
  static getPercentageFlipped() {
    return $(".checked").length / GameCard.numCards * 100;
  }

  /** Uncheck the card 
   *  - Accepts jQuery object
   */
  static uncheckCard($card) {
    $card.prop("checked", false);
  }

  /** Returns boolean showing whether all cards have been flipped */
  static allCardsFlipped() {
    return ($(".matchCard").length === $(".checked").length);
  }

  /** Return a jQuery object of a gamecard */
  static makeGameCard(cardData, id) {
    return $(`
      <input type="checkbox" class="matchCard" id="card-${id}" data-id="${cardData.dataId}" />
      <label for="card-${id}" id="card-label-${id}" class="m-3">
        <div class="label-text">
          ${cardData.text}
        </div>
      </label>`);
  }
}
