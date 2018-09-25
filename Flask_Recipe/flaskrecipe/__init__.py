from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# need to make variable later
app.config['SECRET_KEY'] = '2f2e185f6d5fe7a2e4edbd8db2c42c45'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipeapp.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from flaskrecipe import routes
