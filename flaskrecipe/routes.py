from flask import render_template, url_for, flash, redirect, request, session
from flaskrecipe.forms import RegistrationForm, LoginForm, NewListForm, EnterRecipe, DeleteRecipe, AdditionalListItem, FilterItemForm, SelectRecipe
from flaskrecipe.models import User, Item, List, Recipe, Category, Filter_Item
from flaskrecipe import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import requests
import json
import re

def assign_category(ele):
    # ******************* begin categorizing *******************
    # tokenize ingredient to pick out which words are foods
    words = word_tokenize(ele)

    # filter stop words (of, the, a, ...)
    include_stop_words = set()
    include_stop_words.add('can')
    stop_words = set(stopwords.words('english')) - include_stop_words
    words_filtered = []
    for w in words:
        if w not in stop_words:
            words_filtered.append(w)

    # get synset of each word and store in list
    synset_list = []
    for w in words_filtered:
        syn = set()
        syn = wn.synsets(w)
        if len(syn) > 0:
            synset_list.append(syn[0])
        #print(syn.name())
        #print(syn.definition())

    primary_category = 'Other'

    categories_list = []
    for s in synset_list:
        print(s.definition())
        categories_list.append(categorize(s))

    # some categories will precede others, choose highest
    categories = ''.join(categories_list)
    if 'Canned Goods' in categories:
        primary_category = 'Canned Goods'
    elif 'Frozen Foods' in categories:
        primary_category = 'Frozen Foods'
    else:
        for c in categories_list: # ['Other','Produce', 'Other']
            if c != 'Other':
                primary_category = c
                break
            else:
                primary_category = c

    if primary_category is None:
        primary_category = Category.query.filter_by(name="Other").first()
    else:
        primary_category = Category.query.filter_by(name=primary_category).first()

    return(primary_category.id)
    # ******************* end categorizing *******************

# used in def list to categorize items
def categorize(s):
    category = 'Other'
    # keywords
    meats = ['meat', 'chicken','fish','beef','poultry']
    dairy = ['egg','eggs','milk','cheese','lactose']
    bakery = ['bread','cake','croissants']
    beverages = ['beverage','liquid','juice','water']
    produce = ['fruit','vegetable','plant','garden']
    baking = ['spice','herb','dry','wheat','flour','sugar']

    if 'can' == s.name() or 'canned' == s.name():
        category = 'Canned Goods'
    elif 'frozen' in s.name():
        category = 'Frozen Foods'
    elif any(x in s.definition() for x in meats):
        category = 'Meat'
    elif any(x in s.definition() for x in dairy):
        category = 'Dairy/Eggs'
    elif any(x in s.definition() for x in bakery):
        category = 'Bakery'
    elif any(x in s.definition() for x in beverages):
        category = 'Beverages'
    elif any(x in s.definition() for x in produce):
        category = 'Produce'
    elif any(x in s.definition() for x in baking):
        category = 'Cooking/Baking Goods'
    else:
        category = "Other"
    return category

# Home page will let users create a new list, which will then redirect to MyLists page upon submission
@app.route("/", methods= ['GET','POST'])
@app.route("/home", methods= ['GET','POST'])
def home():
    form = NewListForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        new_list = List(user=current_user, list_title=form.list_title.data)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('mylists'))
    if current_user.is_authenticated == False:
        flash(f'Please login first to create a list', 'info')

    return render_template('home.html', form=form)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/signup", methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, Welcome {form.username.data}!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route("/login", methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        find_user = User.query.filter_by(email=form.email.data).first()
        if find_user and bcrypt.check_password_hash(find_user.password, form.password.data):
            login_user(find_user, remember=form.remember_me.data)
            return redirect(url_for('home'))
        else:
            flash('Email or password is incorrect', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

''' ------------------------------------------------------------------------------------------
MY LISTS PAGE : view all lists and manage filtered ingredients
------------------------------------------------------------------------------------------ '''
@app.route("/myrecipes", methods= ['GET','POST'])
def myrecipes():
    try:
        recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    except:
        recipes = []
        flash(f'No recipes have been saved yet.', 'info')
    return render_template('myrecipes.html', recipes=recipes)

@app.route("/myrecipes/recipe/<recipe_id>", methods= ['GET','POST'])
def recipe(recipe_id):
    try:
        recipe = Recipe.query.filter_by(id=recipe_id).first()
    except:
        recipe = ''
        flash(f'No recipes have been saved yet.', 'info')
    return render_template('myrecipes.html', recipe=recipe)

@app.route("/mylists", methods= ['GET','POST'])
def mylists():
    filter_form = FilterItemForm()
    if filter_form.validate_on_submit and filter_form.submit.data and request.method == 'POST':
        new_filter = Filter_Item(name=filter_form.filter_item.data,user_id=current_user.id)
        db.session.add(new_filter)
        db.session.commit()

    filters = []
    lists = []
    try:
        lists = List.query.filter_by(user_id=current_user.id).all()
        filters = Filter_Item.query.filter_by(user_id=current_user.id).all()

    except:
        flash(f'No lists have been created yet.', 'info')
    return render_template('mylists.html', lists=lists, filters=filters, filter_form=filter_form)

''' ------------------------------------------------------------------------------------------
LISTS PAGE : view items in list
------------------------------------------------------------------------------------------ '''

@app.route("/mylists/list/<list_id>", methods= ['GET','POST'])
def list(list_id):
    if current_user.is_authenticated == False:
        flash(f'Please login', 'info')
        return redirect(url_for('login'))

    # load list
    list_data = List.query.filter_by(id=list_id).first()

    # To add list items in manually
    additional_item = AdditionalListItem()
    if additional_item.validate_on_submit and additional_item.submit_item.data and request.method == 'POST':
        cat_type = assign_category(additional_item.new_item.data)
        new_item = Item(name=additional_item.new_item.data, user=current_user, list_id=list_data.id, category_id=cat_type) #store
        db.session.add(new_item)
        db.session.commit()

    # BEGIN RECIPE WEB SCRAPING
    form = EnterRecipe()
    if form.validate_on_submit and form.submit.data and request.method == 'POST':
        try:
            url = form.recipe_url.data
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers = headers)
            soup = BeautifulSoup(r.text,'html5lib')
            title = soup.title.string

            ld_json = soup.find("script", {"type" : "application/ld+json"}) # METHOD 1: parse for JSON-LD

            if ld_json is not None:
                # if recipeIngredient not found in first block of script, then search next
                failsafe = 0;
                while "recipeIngredient" not in str(ld_json) and failsafe < 10:
                    ld_json = ld_json.findNext("script", {"type": "application/ld+json"})
                    failsafe = failsafe + 1 #provide a failsafe to avoid infinite loop. This occurs if there is no more application/ld_json tags

                # parse out html tags
                ld_json = re.sub(r"<[^>]*>", "", ld_json.string)

                # decode JSON
                items_dict = json.loads(ld_json)
                if ld_json.startswith('[') and ld_json.endswith(']'):
                    items_dict = items_dict[1]

                recipe_list = items_dict["recipeIngredient"]
                recipe_title = soup.title.string
                if recipe_title is None:
                    recipe_title = ''
                #recipe_title = items_dict["headline"]

                recipe_data = Recipe(name=recipe_title, instructions=url, user_id=current_user.id)
                db.session.add(recipe_data)
                db.session.commit()

                # pull each item from dictionary
                for ele in recipe_list:
                    get_category = assign_category(ele)
                    # ******************* begin categorizing *******************
                    # tokenize ingredient to pick out which words are foods
                    words = word_tokenize(ele)

                    # filter stop words (of, the, a, ...)
                    include_stop_words = set()
                    include_stop_words.add('can')
                    stop_words = set(stopwords.words('english')) - include_stop_words
                    words_filtered = []
                    for w in words:
                        if w not in stop_words:
                            words_filtered.append(w)

                    # get synset of each word and store in list
                    synset_list = []
                    for w in words_filtered:
                        syn = set()
                        syn = wn.synsets(w)
                        if len(syn) > 0:
                            synset_list.append(syn[0])
                        #print(syn.name())
                        #print(syn.definition())

                    primary_category = 'Other'

                    categories_list = []
                    for s in synset_list:
                        print(s.definition())
                        categories_list.append(categorize(s))

                    # some categories will precede others, choose highest
                    categories = ''.join(categories_list)
                    if 'Canned Goods' in categories:
                        primary_category = 'Canned Goods'
                    elif 'Frozen Foods' in categories:
                        primary_category = 'Frozen Foods'
                    else:
                        for c in categories_list: # ['Other','Produce', 'Other']
                            if c != 'Other':
                                primary_category = c
                                break
                            else:
                                primary_category = c

                    get_category = Category.query.filter_by(name=primary_category).first()
                    # ******************* end categorizing *******************

                    item = Item(name=ele, user=current_user, list_id=list_id, recipe_id=recipe_data.id, category_id=get_category.id) #store
                    db.session.add(item)
                    db.session.commit()
            else:
                #first store recipe
                recipe_title = soup.title.string
                if recipe_title is None:
                    recipe_title = 'none'
                recipe_data = Recipe(name=recipe_title, instructions=url, user_id=current_user.id)
                db.session.add(recipe_data)
                db.session.commit()

                recipe_list = soup.findAll("li", itemprop=re.compile("\w*([Ii]ngredient)\w*"))

                for ele in recipe_list:
                    # ******************* begin categorizing *******************
                    # tokenize ingredient to pick out which words are foods
                    words = word_tokenize(ele)

                    # filter stop words (of, the, a, ...)
                    include_stop_words = set()
                    include_stop_words.add('can')
                    stop_words = set(stopwords.words('english')) - include_stop_words
                    words_filtered = []
                    for w in words:
                        if w not in stop_words:
                            words_filtered.append(w)

                    # get synset of each word and store in list
                    synset_list = []
                    for w in words_filtered:
                        syn = set()
                        syn = wn.synsets(w)
                        if len(syn) > 0:
                            synset_list.append(syn[0])
                        #print(syn.name())
                        #print(syn.definition())

                    primary_category = 'Other'

                    categories_list = []
                    for s in synset_list:
                        #print(s.definition())
                        categories_list.append(categorize(s))

                    # some categories will precede others, choose highest
                    categories = ''.join(categories_list)
                    if 'Canned Goods' in categories:
                        primary_category = 'Canned Goods'
                    elif 'Frozen Foods' in categories:
                        primary_category = 'Frozen Foods'
                    else:
                        for c in categories_list: # ['Other','Produce', 'Other']
                            if c != 'Other':
                                primary_category = c
                                break
                            else:
                                primary_category = c

                    get_category = Category.query.filter_by(name="Other").first()  #change back to primary_category
                    # ******************* end categorizing *******************
                    item = Item(name=ele.text, user=current_user, list_id=list_id, recipe_id=recipe_data.id, category_id=get_category.id) #store
                    db.session.add(item)
                    db.session.commit()

            # Success if we got to here
            flash(f'Ingredients obtained from {form.recipe_url.data}', 'success')
        except Exception as e:
            print("EXCEPTION")
            print(e)
            flash(f'Cannot obtain ingredients from {form.recipe_url.data}', 'danger')

    items = []
    items = Item.query.filter_by(list_id=list_id).all()

    recipes = []
    for i in items:
        find_recipe = Recipe.query.filter_by(id=i.recipe_id).first()
        if find_recipe not in recipes:
            recipes.append(find_recipe)

    # DELETING RECIPES
    delete_recipe = DeleteRecipe()
    delete_recipe.selected_recipe.choices = recipes #populate drop-down form

    return render_template('list.html', form=form, items=items, delete_recipe=delete_recipe, list_id=list_id, list = list_data, additional_item=additional_item)

    # END RECIPE WEB SCRAPING

''' ------------------------------------------------------------
DELETE RECIPE
--------------------------------------------------------------- '''
@app.route("/delete", methods= ['GET','POST'])
def delete():
    recipe_id = request.form.get('recipe')
    list = request.form.get('list')
    Item.query.filter(Item.recipe_id==recipe_id).delete()
    Recipe.query.filter(Recipe.id==recipe_id).delete()

    db.session.commit()

    flash(f'Deleted recipe', 'success')
    return redirect(url_for('list', list_id=list))

''' ------------------------------------------------------------
CALENDAR
--------------------------------------------------------------- '''
import dateutil
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if date is None:
        return 'None'
    format='%b %d, %Y'
    return date.strftime(format)

@app.route("/calendar")
def calendar():
    select_form = SelectRecipe()
    recipes = []
    recipes_with_dates = []
    try:
        recipes = Recipe.query.filter(User.id==current_user.id).all()
        recipes_with_dates = Recipe.query.filter(User.id==current_user.id, Recipe.plan_date != None).all()
    except Exception as e:
        print(e)

    select_form.selected_recipe.choices = recipes
    return render_template('calendar.html', select_form=select_form, recipes=recipes, recipes_with_dates=recipes_with_dates)
