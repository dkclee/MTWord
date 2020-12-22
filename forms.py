from wtforms import SelectField, StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, Email
from flask_wtf import FlaskForm, RecaptchaField


class SetForm(FlaskForm):
    """Form for adding playlists."""

    name = StringField("Set Name",
                       validators=[InputRequired(),
                                   Length(max=50,
                                          message="Name is too long")
                                   ]
                       )
    description = TextAreaField("Description of the set")


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[Email(),
                                            InputRequired(),
                                            Length(max=50)])
    username = StringField("Username", validators=[InputRequired(),
                                                   Length(max=20)])
    password = PasswordField("Password",
                             validators=[
                                 InputRequired(),
                                 Length(min=6),
                                 ],
                             description="Password must be at least 6 characters long")
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class RequestResetPasswordForm(FlaskForm):
    """Form for resetting the password for the user."""

    email = EmailField("Email", validators=[Email(),
                                            InputRequired(),
                                            Length(max=50)])


class ResetPasswordForm(FlaskForm):
    """Form for resetting the password for the user."""

    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])


class DeleteForm(FlaskForm):
    """ Form used for validation when deleting """
