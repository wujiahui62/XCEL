from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, SelectField, DateTimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address!')

class EditUserForm(FlaskForm):
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')

class EditProfileForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    country = SelectField('Country', choices=[('US', 'The United States'), ('CN', 'China'), ('Other', 'Other')], default='US', validators=[DataRequired()])
    other = StringField('If other, specify the country')
    state = StringField('State')
    city = StringField('City')
    address = StringField('Address')
    zip = StringField('Zip')
    cell = StringField('Phone')
    emergencyContact = StringField('Emergency Contact')
    emergencyPhone = StringField('Emergency Phone')
    healthNotes = TextAreaField('Health Notes')
    submit = SubmitField('Submit')

class EventRegistrationForm(FlaskForm):
    members = SelectField('members', choices=[])
    register = SubmitField('Register')

class LeagueRegistrationForm(FlaskForm):
    teams = SelectField('My Teams', choices=[])
    new_team = StringField('Create a new team')
    register = SubmitField('Register')
    scheduling_requests = TextAreaField('Type your sheduling requests here')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ContactUsForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    address = StringField('Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zip')
    country = SelectField('Country', choices=[('US', 'The United States'), ('CN', 'China'), ('Other', 'Other')], default='US', validators=[DataRequired()])
    other = StringField('Other')
    comments = TextAreaField('Comments', validators=[DataRequired()])
    submit = SubmitField('Submit')

class TopicForm(FlaskForm):
    topic = StringField('Start your topic here', validators=[DataRequired()])
    submit = SubmitField('Submit')