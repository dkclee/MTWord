from flask import Blueprint, jsonify, request

from flask_login import login_required, current_user

from ..helpers.sets import get_esv_text
from ..models import db, Set

api = Blueprint('api', __name__)

####################################################################
# API Verse Routes


@api.route("/api/verse")
def lookup_verse():
    """ Look up the verse with the reference and return JSON """

    reference = request.args["reference"]
    get_verse_num = request.args["get_verse_num"]

    info = get_esv_text(reference, get_verse_num)

    return jsonify(info=info)


####################################################################
# API Verse Routes


@api.route("/api/sets/<set_id>")
def lookup_set(set_id):
    """ Look up the verse with the reference and return JSON """

    current_set = Set.query.get_or_404(set_id)

    cards = [verse.serialize() for verse in current_set.verses]

    return jsonify(cards=cards)


@api.route("/api/sets/<int:set_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(set_id):
    """ Add or Remove a specific set from a user's favorites """

    the_set = Set.query.get(set_id)

    users_favorited_sets = current_user.favorite_sets

    if the_set in users_favorited_sets:
        users_favorited_sets.remove(the_set)
        message = "Removed"
    else:
        users_favorited_sets.append(the_set)
        message = "Added"

    db.session.commit()

    return jsonify(message=message)






