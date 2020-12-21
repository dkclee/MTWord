"use strict";

async function retrieveVerse(verse) {

  let response = await axios.get(API_URL, {
    params: {
      'q': verse,
      'include-headings': false,
      'include-footnotes': false,
      'include-verse-numbers': true,
      'include-short-copyright': false,
      'include-passage-references': false
    },
    headers: {
      'Authorization': API_KEY
    }
  });

  return response;
}


async function getVerseAndChangeSite(evt) {
  
  evt.preventDefault();

  let verse = $("#verse").val();
  console.log(verse);
  let response = await retrieveVerse(verse);

  let verseText = response.data.passages[0];

  console.log(verseText);

  $("#bible-verse").text(verseText);

  $(evt).trigger("reset");
}


$("#verse-form").on("submit", getVerseAndChangeSite);