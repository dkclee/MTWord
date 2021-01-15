
from flask import Blueprint, render_template, flash, redirect, url_for, \
    request, abort

from flask_login import login_user, logout_user, current_user

from flask_mail import Message, Mail

from ..forms import RegisterForm, LoginForm, RequestResetPasswordForm, \
    ResetPasswordForm
from ..models import db, User

from secrets import token_urlsafe

from urllib.parse import urlparse, urljoin

login = Blueprint('login', __name__, template_folder="templates")

mail = Mail()

####################################################################
# Login/Registration Routes


@login.route('/register', methods=["GET", "POST"])
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
        return render_template('login_register/register.html', form=form)

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
        return redirect(url_for("homepage.index"))
    else:
        return render_template("login_register/register.html", form=form)


@login.route("/login", methods=["GET", "POST"])
def handle_login():
    """ Shows the login form or handles logging the user in """

    if current_user.is_authenticated:
        return redirect(url_for("homepage.index"))

    form = LoginForm()

    if form.validate_on_submit():

        # Login and validate the user.
        name = form.username.data
        pwd = form.password.data

        user = User.authenticate(name, pwd)

        if not user:
            form.username.errors = ["Wrong username or password"]
            form.password.errors = ["Wrong username or password"]

            return render_template('login_register/login.html', form=form)

        login_user(user)

        flash('Logged in successfully.', "success")

        next = request.args.get('next')

        # Validate the next url
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('homepage.index'))

    return render_template('login_register/login.html', form=form)


@login.route("/logout")
def logout():
    """ Logs out the user from the webpage """

    logout_user()

    flash('Sucessfully logged out!', "success")

    return redirect(url_for("homepage.index"))


####################################################################
# Reset Password Routes

@login.route("/reset/pw", methods=["GET", "POST"])
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
                            Hello! Your username is {user.username}
                            <hr>
                            <a href="http://localhost:5000/reset/pw/{token}">
                                Click here to change your password
                            </a>
                       </p>"""

        mail.send(msg)

        flash("Email has been sent!")

        return redirect("/")

    return render_template("login_register/request_reset_pw.html", form=form)


@login.route("/reset/pw/<token>", methods=["GET", "POST"])
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

        flash("Your password has been updated!", "success")

        return redirect(url_for("handle_login"))

    return render_template("login_register/reset_pw.html", form=form)


####################################################################
# Helper Function


def is_safe_url(target):
    """ Helper function to determine
        whether the next url is safe
        - Does not allow users to go to a delete route
    """

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc and \
        'delete' not in ref_url.path


def connect_mail(app):
    """ Connect the mail instance to the app """

    mail.init_app(app)