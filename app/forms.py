from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from flask_babel import _, lazy_gettext as _l
from app.models import User
from datetime import datetime


# Übernommen
class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


# Übernommen
class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


# Übernommen
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


# Übernommen
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


# Eigenentwicklung
class TaskForm(FlaskForm):
    # Funktion um das Due Date zu prüfen, dass es nach heute ist
    def validate_newer_than_today(self, due_date):
        if due_date.data and due_date.data < datetime.today().date():
            raise ValidationError('Date must be newer than today!')

    title = StringField(_l('Task Title'), validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField(_l('Description'), validators=[DataRequired(), Length(min=1, max=250)])
    due_date = DateField(_l('Due Date', format='%Y-%m-%d', validators=[DataRequired(), validate_newer_than_today]))
    status = SelectField('Status', choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Done', 'Done')], validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))