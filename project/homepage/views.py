
from flask import Blueprint, render_template, request, url_for, \
    current_app, abort
from flask_login import login_required, current_user
from ..models import Set, db, Verse

from faker import Faker
import cProfile, pstats, io

from functools import wraps

homepage = Blueprint('homepage', __name__)

fake = Faker()


####################################################################
# Route handler decorators

def admin_only(f):
    """ Function decorator to only allow admins to
        view the profiling routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


####################################################################
# Homepage


@homepage.route("/")
def index():
    """ Show the homepage """
    return render_template("home.html")


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
        - If elasticsearch is not available, do a ILIKE
          search through the database
    """
    term = request.args.get('term')
    page = request.args.get('page', 1, type=int)

    if current_app.elasticsearch:
        Set.reindex()

        sets, total = Set.search(term, page, 10)
    else:
        query_term = f"%{term}%"
        sets = Set.query.filter(
            Set.name.ilike(query_term) | Set.description.ilike(query_term)
        ).all()
        total = len(sets)

    next_url = url_for('homepage.search', term=term, page=page + 1) \
        if total > page * 10 else None
    prev_url = url_for('homepage.search', term=term, page=page - 1) \
        if page > 1 else None

    return render_template('search.html', sets=sets, term=term,
                           next_url=next_url, prev_url=prev_url,
                           num_pages=total//10 + 1, page=page)

####################################################################
# Profiling


# @homepage.route("/profile/sets/delete")
# @login_required
# @admin_only
# def delete_all_sets():
#     """ Profile test (only admin can access)
#         - delete all sets
#     """

#     Set.query.delete()
#     db.session.commit()

#     return render_template("home.html")


# @homepage.route("/profile")
# @login_required
# @admin_only
# def search_profile():
#     """ Profile test (only admin can access)
#         - Database ILIKE vs. Elasticsearch
#         - sets: number of sets to make
#         - queries: number of times to search through the db
#     """

#     sets = request.args.get('sets', 500, type=int)
#     queries = request.args.get('queries', 5000, type=int)

#     pr_db = cProfile.Profile()

#     words = []

#     for i in range(sets):
#         words.append(fake.word())
#     #     new_set = Set(name=fake.text(30), description=fake.text())
#     #     db.session.add(new_set)
#     # db.session.commit()

#     pr_es = cProfile.Profile()

#     pr_es.enable()

#     for i in range(queries):
#         term = words[i % sets]
#         new_sets, total = Set.search(term, 1, 10)

#     pr_es.disable()
#     s = io.StringIO()
#     ps = pstats.Stats(pr_es, stream=s).sort_stats("cumtime")
#     ps.print_stats()
#     es_results = s.getvalue()

#     pr_db.enable()

#     for i in range(queries):
#         term = words[i % sets]
#         query_term = f"%{term}%"
#         new_sets = Set.query.filter(
#             Set.name.ilike(query_term) | Set.description.ilike(query_term)
#         ).all()
#         len(new_sets)

#     pr_db.disable()
#     s = io.StringIO()
#     ps = pstats.Stats(pr_db, stream=s).sort_stats("cumtime")
#     ps.print_stats()
#     db_results = s.getvalue()

#     return render_template(
#         'profile.html',
#         db=db_results,
#         es=es_results,
#         sets=sets,
#         queries=queries,)


# @homepage.route("/profile/sets")
# @login_required
# @admin_only
# def make_fake_sets():
#     """ Profile test (only admin can access)
#         - Create fake sets
#     """
#     sets = request.args.get('sets', 500, type=int)

#     for i in range(sets):
#         new_set = Set(name=fake.text(30), description=fake.text())
#         db.session.add(new_set)
#     db.session.commit()

#     return render_template('home.html')


# @homepage.route("/profile/db")
# @login_required
# @admin_only
# def search_with_db():
#     """ Profiling test to show matching terms
#         using the database ILIKE function
#     """
#     pr = cProfile.Profile()

#     page = request.args.get('page', 1, type=int)

#     for i in range(500):
#         new_set = Set(name=fake.text(30), description=fake.text())
#         db.session.add(new_set)
#         db.session.commit()

#     pr.enable()

#     for i in range(5000):
#         term = fake.word()
#         query_term = f"%{term}%"
#         sets = Set.query.filter(
#             Set.name.ilike(query_term) | Set.description.ilike(query_term)
#         ).all()
#         total = len(sets)

#     pr.disable()
#     s = io.StringIO()
#     ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
#     ps.print_stats()
#     print(s.getvalue())

#     next_url = url_for('homepage.search_with_db', term=term, page=page + 1) \
#         if total > page * 10 else None
#     prev_url = url_for('homepage.search_with_db', term=term, page=page - 1) \
#         if page > 1 else None

#     sets = None

#     Verse.query.delete()
#     Set.query.delete()
#     db.session.commit()

#     return render_template('search.html', sets=sets, term=term,
#                            next_url=next_url, prev_url=prev_url,
#                            num_pages=total//10 + 1, page=page)


# @homepage.route("/profile/es")
# @login_required
# @admin_only
# def search_with_elastic():
#     pr = cProfile.Profile()

#     page = request.args.get('page', 1, type=int)

#     for i in range(500):
#         new_set = Set(name=fake.text(30), description=fake.text())
#         db.session.add(new_set)
#         db.session.commit()

#     pr.enable()

#     for i in range(5000):
#         term = fake.word()
#         sets, total = Set.search(term, page, 10)

#     pr.disable()
#     s = io.StringIO()
#     ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
#     ps.print_stats()
#     print(s.getvalue())

#     next_url = url_for('homepage.search_with_db', term=term, page=page + 1) \
#         if total > page * 10 else None
#     prev_url = url_for('homepage.search_with_db', term=term, page=page - 1) \
#         if page > 1 else None

#     sets = None

#     Verse.query.delete()
#     Set.query.delete()
#     db.session.commit()

#     return render_template('search.html', sets=sets, term=term,
#                            next_url=next_url, prev_url=prev_url,
#                            num_pages=total//10 + 1, page=page)
