import os

from project.models import db, Verse

import requests

API_KEY = os.environ.get('API_KEY')
if API_KEY is None:
    from .secret import API_KEY2
    API_KEY = API_KEY2
API_URL = os.environ.get('API_URL', "https://api.esv.org/v3/passage/text/")


def split_verses(verses):
    """ With a string of multiple verses, split on verses

        >>> split_verses("[1] Verse1 [2] Verse2")
        ["Verse1", "Verse2"]
    """

    import re

    verses_list = re.split("\[\d+\]", verses)
    verses_list = [verse.strip() for verse in verses_list if verse.strip()]

    return verses_list


def split_verses_refs(ref, total=0):
    """ If there are references to multiple verses, split them
        "Romans 8:1-3" -> ["Romans 8:1", "Romans 8:2", "Romans 8:3"]

        >>> split_verses_refs("Romans 8:1-3")
        ["Romans 8:1", "Romans 8:2", "Romans 8:3"]

        >>> split_verses_refs("Book 2:4-7")
        ["Book 2:4", "Book 2:5", "Book 2:6", "Book 2:7"]

        >>> split_verses_refs("Book 3", 5)
        ["Book 3:1", "Book 3:2", "Book 3:3", "Book 3:4", "Book 3:5"]
    """
    start_verse = 1

    if ":" in ref:
        split_refs = ref.split(":")

        book_and_chapter = split_refs[0]

        verse_refs = split_refs[1].split("–")

        start_verse = int(verse_refs[0])
        end_verse = int(verse_refs[1])
    else:
        book_and_chapter = ref

        end_verse = total

    full_refs = []

    for i in range(start_verse, end_verse + 1):
        full_refs.append(f"{book_and_chapter}:{i}")

    return full_refs


def get_all_verses(references):
    """ With a list of references, return a list of valid verse instances
        - If verse instances does not exist, create a new one """

    verses = []

    for ref in references:

        get_verse_num = "-" in ref or ":" not in ref

        info = get_esv_text(ref, get_verse_num)

        passages = info['passages']
        reference = info['reference']

        if passages == 'Error: Passage not found':
            continue

        if get_verse_num:
            verse_list = split_verses(passages)

            verse_ref_list = split_verses_refs(reference,
                                               len(verse_list))

            for i in range(len(verse_list)):
                verse = find_or_make_verse(
                    verse_ref_list[i], verse_list[i])
                verses.append(verse)

            continue

        verse = find_or_make_verse(
            reference, passages)

        verses.append(verse)

    return verses


def find_or_make_verse(reference, passages):
    """ Returns a verse instance from the given reference
        - If a verse cannot be found, a new verse is made
    """
    
    verse = Verse.query.filter_by(reference=reference).first()

    if not verse:
        verse = Verse(
            reference=reference,
            verse=passages
        )
        db.session.add(verse)
        db.session.commit()

    return verse


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
        'indent-poetry-lines': 0,
        'indent-paragraphs': 0,
        'indent-declares': 0,
        'indent-psalm-doxology': 0,
    }

    headers = {
        'Authorization': f'Token {API_KEY}'
    }

    response = requests.get(API_URL, params=params, headers=headers)

    passages = response.json()['passages']
    reference = response.json()["query"]

    return {
        'passages': passages[0].strip()
        if passages else 'Error: Passage not found',
        'reference': reference
    }
