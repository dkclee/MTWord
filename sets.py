from secret import API_KEY, API_URL

import requests


def get_all_verses(references):
    """ With a list of verse references, get all the verses """

    for refs in references:
        if "-" in refs:
            refs = split_verses(refs)
        else:
            refs = [refs]

        for ref in refs:
            verse = get_esv_text(ref)

    return False


def split_verses(ref):
    """ If there are references to multiple verses, split them
        "Romans 8:1-3" -> ["Romans 8:1", "Romans 8:2", "Romans 8:3"]
    """


def get_esv_text(passage, get_verse_num=False):
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

    # return response.json()

    return passages[0].strip() if passages else 'Error: Passage not found'
