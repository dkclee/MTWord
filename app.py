import os

from flask import Flask, redirect, render_template, session, flash, request, abort, url_for, Markup
from flask_debugtoolbar import DebugToolbarExtension

from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_bootstrap import Bootstrap

from models import db, connect_db, User, UserSet, Set, SetVerse, Verse
from forms import RegisterForm, LoginForm, DeleteForm, ResetPasswordForm, RequestResetPasswordForm

from secrets import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY

import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bible_memorization'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY

debug = DebugToolbarExtension(app)

connect_db(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "handle_login"
login_manager.login_message = "Please log in!"


class MTWordModelView(ModelView):
    def is_accessible(self):
        if current_user.is_anonymous:
            return False

        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_anonymous:
            return False

        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))


admin = Admin(app,
              name='MTWord',
              template_mode='bootstrap3',
              index_view=MyAdminIndexView())
app.config['FLASK_ADMIN_SWATCH'] = 'journal'


# Administrative views
admin.add_view(MTWordModelView(User, db.session))
admin.add_view(MTWordModelView(Set, db.session))

app.run()

db.create_all()


####################################################################
# Setting up Login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


####################################################################
# Homepage


@app.route("/")
def index():
    """ """
    return render_template("base.html")


####################################################################
# Login/Registration Routes


@app.route('/register', methods=["GET", "POST"])
def handle_registration():
    """ Show the registration form or handles the registration
        of a user, if the email or username is taken, take them back to the
        registration form
        - Upon successful login, take to the homepage
    """

    form = RegisterForm()

    email = form.email.data
    username = form.username.data

    # If there is a user with this email already
    if User.query.filter_by(email=email).first():
        form.email.errors = ["This email is already being used"]

    # Check if there is a user with this username already
    if User.query.filter_by(username=username).first():
        form.username.errors = ["This username is already being used"]

    if form.email.errors or form.username.errors:
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        pwd = form.password.data
        f_name = form.first_name.data
        l_name = form.last_name.data

        user = User.register(username=username,
                             pwd=pwd,
                             email=email,
                             f_name=f_name,
                             l_name=l_name)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Sucessfully logged in!', "success")

        # on successful login, redirect to user detail page
        return redirect(url_for("index"))
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def handle_login():
    """ Shows the login form or handles logging the user in """

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        # Login and validate the user.
        name = form.username.data
        pwd = form.password.data

        user = User.authenticate(name, pwd)

        if not user:
            form.username.errors = ["Wrong username or password"]
            form.password.errors = ["Wrong username or password"]

            return render_template('login.html', form=form)

        # user should be an instance of your `User` class
        login_user(user)

        flash('Logged in successfully.')

        return redirect(url_for('index'))

        # next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #     return abort(400)

    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    """ Logs out the user from the webpage """

    logout_user()

    flash('Sucessfully logged out!', "success")

    return redirect(url_for("index"))


@app.route("/helo")
@login_required
def hello():
    return "hello"


####################################################################
