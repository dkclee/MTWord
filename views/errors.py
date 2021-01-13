
from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


####################################################################
# Error Pages

@errors.errorhandler(404)
def show_404_page(err):
    return render_template('errors/404.html'), 404


@errors.errorhandler(401)
def show_401_page(err):
    return render_template('errors/401.html'), 401
