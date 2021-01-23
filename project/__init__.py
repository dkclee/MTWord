import os, re

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from flask_login import LoginManager

from flask_admin import Admin

from project.admin import MyAdminIndexView, MTWordModelView

from flask_bootstrap import Bootstrap

from elasticsearch import Elasticsearch

from project.models import db, connect_db, User, Set, Verse

from .api.views import api
from .login.views import login, connect_mail
from .sets.views import sets
from .users.views import users
from .homepage.views import homepage

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bible_memorization'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get(
    'RECAPTCHA_PUBLIC_KEY',
    "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get(
    'RECAPTCHA_PRIVATE_KEY',
    "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu")

bonsai = None

if os.environ.get('FLASK_ENV', None) == 'production':
    # Parse the auth and host from env:
    bonsai = os.environ['ELASTICSEARCH_URL']
    auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
    host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

    app.config['ELASTICSEARCH_URL'] = bonsai

    # Connect to cluster over SSL using auth for best security:
    es_header = [{
        'host': host,
        'port': 443,
        'use_ssl': True,
        'http_auth': (auth[0], auth[1])
    }]

    # Instantiate the new Elasticsearch connection:
    app.elasticsearch = Elasticsearch(es_header) if bonsai else None
else:
    app.config['ELASTICSEARCH_URL'] = "http://localhost:9200"
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

debug = DebugToolbarExtension(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login.handle_login"
login_manager.login_message = "Please log in!"

admin = Admin(app,
              name='MTWord',
              template_mode='bootstrap3',
              index_view=MyAdminIndexView())
app.config['FLASK_ADMIN_SWATCH'] = 'journal'

# Administrative views
admin.add_view(MTWordModelView(User, db.session))
admin.add_view(MTWordModelView(Set, db.session))
admin.add_view(MTWordModelView(Verse, db.session))

app.config.update(
    {
        "MAIL_SERVER": os.environ.get("MAIL_SERVER"),
        "MAIL_PORT": os.environ.get("MAIL_PORT"),
        "MAIL_USE_TLS": os.environ.get("MAIL_USE_TLS"),
        "MAIL_USE_SSL": os.environ.get("MAIL_USE_SSL"),
        "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
        "MAIL_DEFAULT_SENDER": os.environ.get("MAIL_DEFAULT_SENDER"),
        "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD")
    }
)
connect_mail(app)

db.create_all()

app.register_blueprint(api)
app.register_blueprint(homepage)
app.register_blueprint(login)
app.register_blueprint(sets)
app.register_blueprint(users)


####################################################################
# Setting up Login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

####################################################################
# Error Pages


@app.errorhandler(404)
def show_404_page(err):
    return render_template('errors/404.html'), 404


@app.errorhandler(401)
def show_401_page(err):
    return render_template('errors/401.html'), 401
