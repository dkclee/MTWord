"use strict";

const FAVORITES_URL = function(set_id) {
  return `/api/sets/${set_id}/favorite`
} 

const $carousel = $("#set-carousel");

/** Make the first card active so that the 
 *  carousel will function properly
 */

function makeFirstCardActive(evt) {
  $(".carousel-item").first().addClass("active");
}

$(document).ready(makeFirstCardActive);


/** Flips the card when the card is clicked */

function handleFlipCard(evt) {
  let $cardBody = $(".active").children().children().first();

  if ($cardBody.hasClass("flipped")) {
    $cardBody.removeClass("flipped");
  } else {
    $cardBody.addClass("flipped");
  }
}

$carousel.on("click", ".card-body", handleFlipCard);


/** Handles keypress in order to flip the card
 *  or to shuffle through cards
 */
function handleKeyPress(evt) {
  if(evt.code === "ArrowDown" || evt.code === "ArrowUp" || evt.code === "Space") {
    evt.preventDefault();
    handleFlipCard()
  } else if(evt.code === "ArrowRight") {
    evt.preventDefault();
    $carousel.carousel('next')
  } else if(evt.code === "ArrowLeft") {
    evt.preventDefault();
    $carousel.carousel('prev')
  }
}


$(document).on("keydown", handleKeyPress)


/** Toggle favorites 
 *  - Make an API call to change database
 *  - Change the button color (success to warning & 
 *    vice versa)
 */

async function toggleFavorites(evt) {
  let $favBtn = $("#favoriteSetBtn");

  let set_id = $favBtn.data("set_id");

  let resp = await axios.post(FAVORITES_URL(set_id));

  let msg = resp.data.message;

  if (msg === "Added") {
    $("#favoriteSetBtnText").text("Unfavorite this set")
  } else {
    $("#favoriteSetBtnText").text("Favorite this set")
  }

  $favBtn.toggleClass("btn-outline-success");
  $favBtn.toggleClass("btn-outline-warning");

}


$("#favoriteSetBtn").on("click", toggleFavorites);
