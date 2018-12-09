from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskrecipe.models import User, Recipe

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

class NewListForm(FlaskForm):
    list_title = StringField('List Name', validators=[DataRequired()])
    submit = SubmitField('Create List')

class EnterRecipe(FlaskForm):
    recipe_url = StringField('Recipe URL', validators=[DataRequired()])
    submit = SubmitField('Get Ingredients')

class DeleteRecipe(FlaskForm):
    selected_recipe = SelectField(u'Recipes',coerce=int)
    delete = SubmitField('Delete Recipe')

class AdditionalListItem(FlaskForm):
    new_item = StringField('New Item', validators=[DataRequired()])
    submit_item = SubmitField('Add Item')

class FilterItemForm(FlaskForm):
    filter_item = StringField('Add Filters', validators=[DataRequired()])
    submit_filter = SubmitField('Submit')

class DeleteFilterForm(FlaskForm):
    delete_filter = SubmitField('Remove Filters')

class SelectRecipe(FlaskForm):
    selected_recipe = SelectField(u'Recipes',coerce=int)
    submit = SubmitField('Add Recipe')
