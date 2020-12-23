"use strict";

const $carousel = 

/** Make the first card active so that the 
 *  carousel will function properly
 */

function makeFirstCardActive(evt) {
  $(".carousel-item").first().addClass("active");
}

$(document).ready(makeFirstCardActive);



$()