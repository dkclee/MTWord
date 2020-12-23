from secret import API_KEY, API_URL

from models import db, Verse

import requests

# TODO: If you get a list of verses, convert them to individual instances

# def get_all_verses(references):
#     """ With a list of verse references, get all the verses """

#     for refs in references:
#         if "-" in refs:
#             refs = split_verses(refs)
#         else:
#             refs = [refs]

#         for ref in refs:
#             verse = get_esv_text(ref)

#     return False


# def split_verses(ref):
#     """ If there are references to multiple verses, split them
#         "Romans 8:1-3" -> ["Romans 8:1", "Romans 8:2", "Romans 8:3"]
#     """

#     split_refs = ref.split(":")

#     ref_arr 

def get_all_verses(references):
    """ With a list of references, return a list of valid verse instances
        - If verse instances does not exist, create a new one """

    verses = []

    for ref in references:

        info = get_esv_text(ref, False)

        passages = info['passages']
        reference = info['reference']

        if passages == 'Error: Passage not found':
            continue

        verse = Verse.query.filter_by(reference=reference).first()

        if not verse:
            verse = Verse(
                reference=reference,
                verse=passages
            )
            db.session.add(verse)
            db.session.commit()

        verses.append(verse)

    return verses


def get_esv_text(passage, get_verse_num=True):
    """ Get the esv text from the API """

    params = {
        'q': passage,
        'include-headings': False,
        'include-footnotes': False,
        'include-verse-numbers': get_verse_num,
        'include-short-copyright': False,
        'include-passage-references': False,
        'indent-poetry': False,
    }

    headers = {
        'Authorization': f'Token {API_KEY}'
    }

    response = requests.get(API_URL, params=params, headers=headers)

    passages = response.json()['passages']
    reference = response.json()["query"]

    # return response.json()

    return {
        'passages': passages[0].strip() if passages else 'Error: Passage not found',
        'reference': reference
    }
