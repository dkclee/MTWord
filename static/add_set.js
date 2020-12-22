"use strict";

const VERSE_API = "/api/verse"

/** Generator to make sure to get the 
 *  snext value for the verse field id's */

function* infinite() {
  let index = 1;

  while (true) {
      yield index++;
  }
}

const generator = infinite(); 


/** Add another verse field unto the form */

function addFields(evt) {

  let newField = generateVerseField(generator.next().value);
  
  $("#verseFields").append(newField);

}

/** Helper function to generate one of the 
 *  fields for a verse and reference */

function generateVerseField(num) {
  return $(`<div class="form-group row verseField align-items-center">
              <div class="col">
                  <input class="form-control input-ref" id="ref-${num}" name="refs" required="" type="text" value="">
              </div>
              <div class="col">
                  <textarea cols="35" rows="4" id="verse-${num}" disabled></textarea>
              </div>
              <div class="delete-field col-lg-1">
                  <button class="btn btn-sm btn-danger" type="button">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill" viewBox="0 0 16 16">
                          <path fill-rule="evenodd" d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5a.5.5 0 0 0-1 0v7a.5.5 0 0 0 1 0v-7z"/>
                      </svg>
                  </button>
              </div>
            </div>`)
}

$("#addFields").on("click", addFields)



async function refreshVerseFields(evt) {
  const $input = $(evt.target);
  const targetId = $input.attr('id').split("-")[1];

  const reference = $input.val();

  const verse = await retrieveVerse(reference);

  $(`#verse-${targetId}`).val(verse);

}


async function retrieveVerse(reference) {
  let resp = await axios.get(VERSE_API, {
    params: {
      "reference": reference, 
      "get_verse_num": true
    }
  });

  return resp.data.verse;
}




$('#verseFields').on("input", ".input-ref", _.debounce(refreshVerseFields, 750));














/** Delete one of the verse fields */

function deleteVerseField(evt) {
  let $trashButton = $(evt.target)

  $trashButton.closest(".verseField").remove()
}

$("#verseFields").on("click", ".delete-field", deleteVerseField)