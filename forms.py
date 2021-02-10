from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class UserForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(), Length(min=0, max=20, message='Length is no longer 20 chars')])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Must be a valid email'), Length(min=0, max=50, message='Length is no longer than 50 chars')])
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=0, max=30, message='Length is no longer 30 chars')])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=0, max=30, message='Length is no longer 30 chars')])

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(), Length(min=0, max=20, message='Length is no longer 20 chars')])
    password = PasswordField('Password', validators=[InputRequired()])

class FeedbackForm(FlaskForm):

    title = StringField('Title', validators=[InputRequired(), Length(min=0, max=100, message='Length is no longer 100 chars')])
    content = TextAreaField('Content', validators=[InputRequired()])