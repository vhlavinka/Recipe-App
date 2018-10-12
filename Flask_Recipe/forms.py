from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])
    reenter = PasswordField('Re-enter password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    session = BooleanField('Remember me')

    submit = SubmitField('Sign in')

class EnterRecipe(FlaskForm):
    recipe_url = StringField('Recipe URL', validators=[DataRequired()])

    submit = SubmitField('Get Ingredients')
