"use strict";

const BASE_URL = "/api/sets";
const SET_ID = $("#setId").val();;
const MAX_CARDS = 6;
const TOTAL_SECONDS = 30;
let verses;
let numCards;
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
  $gameBoard.empty();

  await getNewVerses();
  makeCards();

  $("#progressBar").css("width", `0%`);

  timerInterval = resetTimer(TOTAL_SECONDS);

  $gameBoardContainer.removeClass("d-none");
}

/** Game controller
 *  - Called when the user clicks the button to replay the game 
 *    on the modal
 */
async function startGameFromModal(evt) {
  $gameFinishedModal.modal("hide");
  $gameBoard.empty();

  if (verses.length === 0) await getNewVerses();

  $("#progressBar").css("width", `0%`);
  timerInterval = resetTimer(TOTAL_SECONDS);

  makeCards();
}

$gameStartForm.on("submit", startGameWithForm);
$playAgainBtn.on("click", startGameFromModal);

/** Main functionality of the game
 *  - if the two id's match, add a checked class to the label
 *    then disable the checking
 * 
 *  Check to see if the game has finished at the end
 */

function checkCards(evt) {
  let $checkedCards = $('input:checked');

  if ($checkedCards.length > 1) {
    let $card1 = $($checkedCards[0]);
    let $card2 = $($checkedCards[1]);

    // If the cards have the same id (verse and ref match)
    // - grab the card Id's
    // - change the labels to checked (turns green)
    // - disable the checkboxes
    // - uncheck the checkboxes 
    // - update progress bar
    if ($card1.data("id") === $card2.data("id")) {
      let card1Id = $card1.attr('id').split("-")[1];
      let card2Id = $card2.attr('id').split("-")[1];

      $(`#card-label-${card1Id}`).addClass("checked");
      $(`#card-label-${card2Id}`).addClass("checked");

      $card1.attr("disabled", true);
      $card2.attr("disabled", true);
    }

    $('input:checked').prop("checked", false);
    $(evt.target).prop("checked", false);

    let progressPercent = Math.floor(
      $(".checked").length / numCards * 100
    );
    $("#progressBar").css("width", `${progressPercent}%`);
  }

  if ($(".matchCard").length === $(".checked").length) {
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
    cardsToMake.push({ id: i, text: verse });
    cardsToMake.push({ id: i, text: reference });
  };

  numCards = cardsToMake.length;

  cardsToMake = _.shuffle(cardsToMake);

  for (let j = 0; j < cardsToMake.length; j++) {
    let cardData = cardsToMake[j];
    $gameBoard.append($(`
        <input type="checkbox" class="matchCard" id="card-${j}" data-id="${cardData.id}" />
        <label for="card-${j}" id="card-label-${j}" class="m-3">
          <div class="label-text">
            ${cardData.text}
          </div>
        </label>`));
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
 

