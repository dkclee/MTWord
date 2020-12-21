from flask import Flask, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension

from flask_bootstrap import Bootstrap

from models import db, connect_db, User, UserSet, Set, SetVerse, Verse
from forms import RegisterForm, LoginForm, DeleteForm, ResetPasswordForm, RequestResetPasswordForm
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bible_memorization'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
Bootstrap(app)

db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def root():
    """ """
    return render_template("base.html")


@app.route('/register', methods=["GET", "POST"])
def handle_registration():
    """ Show the registration form or handles the registration
        of a user, if the email is taken, take them back to the
        registration form
        - If someone is already logged in, redirect to their page
    """

    username = session.get("user_id")

    if username:
        return redirect(f"/users/{username}")

    form = RegisterForm()

    email = form.email.data

    # If there is a user with this email already
    if User.query.filter_by(email=email).first():
        form.email.errors = ["This email is already being used"]
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        f_name = form.first_name.data
        l_name = form.last_name.data

        user = User.register(name, pwd, email, f_name, l_name)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.username

        # on successful login, redirect to user detail page
        return redirect(f"/users/{user.username}")
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def handle_login():
    """ Shows the login form or handles logging the user in """

    username = session.get("user_id")

    if username:
        return redirect(f"/users/{username}")

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["user_id"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """ Logs out the user from the webpage """

    if session.pop("user_id", None):
        flash("You have been logged out!")
    else:
        flash("No user logged in!")

    return redirect("/login")