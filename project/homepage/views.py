
from flask import Blueprint, render_template, request, url_for
from ..models import Set

homepage = Blueprint('homepage', __name__)


####################################################################
# Homepage


@homepage.route("/")
def index():
    """ Show the homepage """
    return render_template("base.html")


@homepage.route("/explore")
def explore():
    """ Show the most recent sets
        - Paginate with each page having 10 sets
    """

    page = request.args.get('page', 1, type=int)
    sets = Set.query.order_by(Set.created_at.desc()).paginate(page, 10)

    return render_template("explore.html", sets=sets.items, set_paginate=sets)


@homepage.route("/search")
def search():
    """ Show the sets matching the searched terms
        - Show 10 and paginate
    """
    term = request.args.get('term')
    page = request.args.get('page', 1, type=int)

    Set.reindex()

    sets, total = Set.search(term, page, 10)

    next_url = url_for('homepage.search', term=term, page=page + 1) \
        if total > page * 10 else None
    prev_url = url_for('homepage.search', term=term, page=page - 1) \
        if page > 1 else None

    return render_template('search.html', sets=sets, term=term,
                           next_url=next_url, prev_url=prev_url,
                           num_pages=total//10 + 1, page=page)
