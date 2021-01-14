import os

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from flask_login import LoginManager, login_manager

from flask_admin import Admin

from project.admin import MyAdminIndexView, MTWordModelView

from flask_mail import Mail

from flask_bootstrap import Bootstrap

from elasticsearch import Elasticsearch

from project.models import db, connect_db, User, Set, Verse

from project.secret import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, mail_settings

from .api.views import api
from .login.views import login
from .sets.views import sets
from .users.views import users
from .homepage.views import homepage

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bible_memorization'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY


app.config['ELASTICSEARCH_URL'] = os.environ.get('ELASTICSEARCH_URL')
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

debug = DebugToolbarExtension(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "handle_login"
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

app.config.update(mail_settings)
mail = Mail(app)

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

