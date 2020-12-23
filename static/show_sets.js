"use strict";

const $carousel = $("#set-carousel");

/** Make the first card active so that the 
 *  carousel will function properly
 */

function makeFirstCardActive(evt) {
  $(".carousel-item").first().addClass("active");
}

$(document).ready(makeFirstCardActive);





function handleFlipCard(evt) {
  let $cardBody = $(evt.target).closest(".card-body");

  console.log($cardBody);

  if ($cardBody.hasClass("flipped")) {
    $cardBody.removeClass("flipped");
  } else {
    $cardBody.addClass("flipped");
  }
}


$carousel.on("click", ".card-body", handleFlipCard);