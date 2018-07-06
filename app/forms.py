from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, SelectField, DateTimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

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

class EditProfileForm(FlaskForm):
    fname = StringField('fname', validators=[DataRequired()])
    lname = StringField('lname', validators=[DataRequired()])
    gender = RadioField('gender', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    # birthday = DataRequired('birthday', format='%m/%d/%y', validators=[DataRequired()])
    country = SelectField('country', choices=['China', 'The United States', 'Other'], validators=[DataRequired()])
    state = StringField('state')
    city = StringField('city')
    address = TextAreaField('address')
    zip = StringField('zip')
    cell = StringField('cell')
    healthNotes = TextAreaField('healthNotes')
    emergencyContact = StringField('emergencyContact')
    emergencyPhone = StringField('emergencyPhone')
    submit = SubmitField('Submit')
