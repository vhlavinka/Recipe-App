from flaskrecipe import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)
    # One User may belong to many lists
    lists = db.relationship('List', backref='user', lazy=True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=True) # does not have to belond to a recipe
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    checked = db.Column(db.Integer, default=0)
    # one to one with Recipe_Ingredients
    #recipe = db.relationship('Recipe_Ingredients', backref='recipe_item', lazy=True, uselist=False)
    # One item belongs to one list
    #list = db.relationship('List_Items', backref='item', lazy=True, uselist=False)
    def __repr__(self):
        return f"Item('{self.id}', '{self.name}','{self.recipe_id}')"

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    list_title = db.Column(db.String(200))
    items = db.relationship('Item', backref='list_item', lazy=True)
    # add in date columns so the list can be used as meal plan

    # One List belongs to many items
    #items = db.relationship('List_Items', backref='list_item', lazy=True)
    def __repr__(self):
        return f"List('{self.id}', '{self.user_id}', '{self.list_title}')"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(500))
    # replace instructions with url to original recipe
    instructions = db.Column(db.String(5000))
    ingredients = db.relationship('Item', backref='ingredient', lazy=True) # one recipe may have many ingredients
    #ingredients = db.relationship('Recipe_Ingredients', backref='recipe', lazy=True) # one recipe may have many ingredients
    def __repr__(self):
        return f"Recipe('{self.id}', '{self.name}')"
'''
class Recipe_Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    measurements = db.Column(db.String(20))
    def __repr__(self):
        return f"Recipe_Ingredients('{self.id}', '{self.recipe_id}', '{self.item_id}')"


class List_Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)#no
    checked = db.Column(db.Integer, default=0)
    def __repr__(self):
        return f"List_Items('{self.id}','{self.list_id}','{self.item_id}','{self.checked}')"
'''
