"use strict";

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

  if(evt.code === "ArrowDown" || evt.code === "ArrowUp") {
    handleFlipCard()
  } else if(evt.code === "ArrowRight") {
    $carousel.carousel('next')
  } else if(evt.code === "ArrowLeft") {
    $carousel.carousel('prev')
  }
}


$(document).on("keydown", handleKeyPress)
