from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskrecipe.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])
    reenter = PasswordField('Re-enter password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign up')

    def validate_username(self, username):
        find_user = User.query.filter_by(username=username.data).first()
        if find_user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        find_email = User.query.filter_by(email=email.data).first()
        if find_email:
            raise ValidationError('Email already exists.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')

    submit = SubmitField('Sign in')

class EnterRecipe(FlaskForm):
    recipe_url = StringField('Recipe URL', validators=[DataRequired()])

    submit = SubmitField('Get Ingredients')
