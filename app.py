import os

from flask import Flask, redirect, render_template, session, flash, request, abort, url_for
from flask_debugtoolbar import DebugToolbarExtension

from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_bootstrap import Bootstrap

from models import db, connect_db, User, UserSet, Set, SetVerse, Verse
from forms import RegisterForm, LoginForm, DeleteForm, ResetPasswordForm, RequestResetPasswordForm

from secret import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, EMAIL_PASSWORD, EMAIL_USER

from secrets import token_urlsafe

from flask_mail import Mail, Message

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


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": EMAIL_USER,
    "MAIL_DEFAULT_SENDER": EMAIL_USER,
    "MAIL_PASSWORD": EMAIL_PASSWORD
}

app.config.update(mail_settings)
mail = Mail(app)


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


db.create_all()


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
        return render_template("login_register/register.html", form=form)


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

        login_user(user)

        flash('Logged in successfully.')

        return redirect(url_for('index'))

    return render_template('login_register/login.html', form=form)


@app.route("/logout")
def logout():
    """ Logs out the user from the webpage """

    logout_user()

    flash('Sucessfully logged out!', "success")

    return redirect(url_for("index"))


####################################################################
# Reset Password Route

@app.route("/reset/pw", methods=["GET", "POST"])
def request_reset_pw():

    form = RequestResetPasswordForm()
    email = form.email.data

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()

        if not user:
            form.email.errors = ["No user found with this email"]
            return render_template("request_reset_pw.html", form=form)

        token = token_urlsafe(16)

        user.password_reset_token = token

        db.session.commit()

        msg = Message("Your password token",
                      recipients=[email])
        msg.html = f"""<p>
                            <a href="http://localhost:5000/reset/pw/{token}">
                                Click here to change your password
                            </a>
                       </p>"""

        mail.send(msg)

        flash("Email has been sent!")

        return redirect("/")

    return render_template("login_register/request_reset_pw.html", form=form)


@app.route("/reset/pw/<token>", methods=["GET", "POST"])
def reset_pw(token):

    form = ResetPasswordForm()
    user = User.query.filter_by(password_reset_token=token).first()

    if not user:
        abort(404)

    if form.validate_on_submit():
        password = form.password.data

        user.update_password(password)

        user.password_reset_token = None

        db.session.commit()

        flash("Your password has been updated!")

        return redirect("/login")

    return render_template("login_register/reset_pw.html", form=form)


####################################################################
# User Routes

@app.route("/users/<int:user_id>")
def show_user_profile(user_id):
    """ Shows the user profile """


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user_profile(user_id):
    """ Shows the user profile """


####################################################################
# Set Routes


@app.route("/sets/new", methods=["GET", "POST"])
@login_required
def create_new_set():
    """ Creates a new set """

    form = 


@app.route("/sets/<int:set_id>")
def show_set(set_id):
    """ Show the set """


@app.route("/sets/<int:set_id>/test")
def show_set_test(set_id):
    """  """


@app.route("/sets/<int:set_id>/cards")
def show_set_cards(set_id):
    """ """

####################################################################
# API Verse Routes


@app.route("/api/verse/<ref>", methods=["GET", "POST"])
def lookup_verse(ref):
    """ Look up the verse with the reference and return JSON """

