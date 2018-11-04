''' ================================================================
Delete recipeapp.db to reset the database
Run this to create the tables and populate Category data
Re-create users on front end
================================================================ '''

from flaskrecipe.models import User, Item, List, Recipe, Category, Filter_Item

# create all tables
db.create_all()

# populate Category table with appropriate categories
cat_1 = Category(name="Other")
cat_2 = Category(name="Canned Goods")
cat_3 = Category(name="Frozen Foods")
cat_4 = Category(name="Meat")
cat_5 = Category(name="Dairy/Eggs")
cat_6 = Category(name="Bakery")
cat_7 = Category(name="Beverages")
cat_8 = Category(name="Produce")
cat_9 = Category(name="Cooking/Baking")

# add each category
db.session.add(cat_1)
db.session.add(cat_2)
db.session.add(cat_3)
db.session.add(cat_4)
db.session.add(cat_5)
db.session.add(cat_6)
db.session.add(cat_7)
db.session.add(cat_8)
db.session.add(cat_9)

# commit changes
db.session.commit()
