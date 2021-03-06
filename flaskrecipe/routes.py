from flask import render_template, url_for, flash, redirect, request, session
from flaskrecipe.forms import *
from flaskrecipe.models import User, Item, Grocerylist, Recipe, Category, Filter_Item
from flaskrecipe import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import requests
import json
import re
from datetime import datetime
import dateutil

''' ===========================================================================================
PAGE home : summary of how to get started and create a new list here
=========================================================================================== '''
@app.route("/", methods= ['GET','POST'])
@app.route("/home", methods= ['GET','POST'])
def home():
    form = NewListForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        new_list = Grocerylist(user=current_user, list_title=form.list_title.data)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('mylists'))
    if form.validate_on_submit() and current_user.is_authenticated == False:
        flash(f'Please register or login first to create a list', 'info')
        return redirect(url_for('register'))

    return render_template('home.html', form=form)

@app.route("/about")
def about():
    return render_template('about.html')

''' ===========================================================================================
PAGE signup and login : basic login and sign functionality
=========================================================================================== '''
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

''' ===========================================================================================
PAGE mylists : all of a user's lists can be viewed here
=========================================================================================== '''
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
    # redirect if user not logged in
    if current_user.is_authenticated == False:
        flash(f'Please login', 'info')
        return redirect(url_for('login'))

    # form for adding items that the user wants to filter
    filter_form = FilterItemForm()
    if filter_form.validate_on_submit and filter_form.submit_filter.data and request.method == 'POST':
        if filter_form.data is not None:
            new_filter = Filter_Item(name=filter_form.filter_item.data,user_id=current_user.id)
            db.session.add(new_filter)
            db.session.commit()

    # form for deleting filtered items from list
    delete_filter_form = DeleteFilterForm()
    if delete_filter_form.validate_on_submit and delete_filter_form.delete_filter.data and request.method == 'POST':
        delete_filters = request.form.getlist('check')
        delete_filter_query = Filter_Item.query.filter(Filter_Item.name.in_(delete_filters)).filter(Filter_Item.user_id == current_user.id).all()
        for dfq in delete_filter_query:
            Filter_Item.query.filter(Filter_Item.id == dfq.id).delete()
        db.session.commit()

    # form for creating a new list
    form = NewListForm()
    if form.validate_on_submit() and form.submit.data and current_user.is_authenticated and request.method =='POST':
        new_list = Grocerylist(user=current_user, list_title=form.list_title.data)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('list', list_id=new_list.id))

    # form for deleting LISTS
    delete_list_form = DeleteListForm()
    if delete_list_form.validate_on_submit and delete_list_form.delete_list.data and current_user.is_authenticated and request.method =='POST':
        delete_lists = request.form.getlist('checklist')
        delete_list_query = Grocerylist.query.filter(Grocerylist.id.in_(delete_lists)).filter(Grocerylist.user_id == current_user.id).all()

        # temporarily store list_id
        list_ids = []

        # delete each checked list
        for dlq in delete_list_query:
            list_ids.append(dlq.id)
            Grocerylist.query.filter(Grocerylist.id == dlq.id).delete()
            db.session.commit()

        # delete items associated with list as well
        print(list_ids)
        for lid in list_ids:
            delete_items_query = Item.query.filter(Item.list_id==lid).all()
            print(delete_items_query)
            for diq in delete_items_query:
                Item.query.filter(Item.id == diq.id).delete()
                db.session.commit()

    filters = []
    lists = []
    try:
        lists = Grocerylist.query.filter_by(user_id=current_user.id).all()
        filters = Filter_Item.query.filter_by(user_id=current_user.id).all()
    except:
        flash(f'No lists have been created yet.', 'info')

    return render_template('mylists.html', lists=lists, filters=filters, filter_form=filter_form,
    delete_filter_form = delete_filter_form, delete_list_form=delete_list_form, form=form)

''' ===========================================================================================
FUNCTION categorize : assigns a category to an ingredient
=========================================================================================== '''
# used in def list to categorize items
def categorize(syn):
    s = wn.synsets(syn)
    if len(s) > 0:
        s = s[0]
    else:
        return 'Other'

    # keywords
    meats = ['meat', 'chicken','fish','beef','poultry']
    dairy = ['egg','eggs','milk','cheese','lactose']
    bakery = ['bread','cake','croissants']
    beverages = ['beverage','liquid','juice','water']
    produce = ['fruit','vegetable','plant','garden']
    baking = ['spice','herb','dry','wheat','flour','sugar','baking','flavor', 'season','powder']

    # check each list of keywords to see where ingredient fits best
    if 'can' == s.name() or 'canned' == s.name():
        category = 'Canned Goods'
    elif 'frozen' in s.name():
        category = 'Frozen Foods'
    elif any(x in s.definition() for x in baking):
        category = 'Cooking/Baking'
    elif any(x in s.definition() for x in produce):
        category = 'Produce'
    elif any(x in s.definition() for x in dairy):
        category = 'Dairy/Eggs'
    elif any(x in s.definition() for x in meats):
        category = 'Meat'
    elif any(x in s.definition() for x in bakery):
        category = 'Bakery'
    elif any(x in s.definition() for x in beverages):
        category = 'Beverages'
    else:
        category = 'Other'

    # print (s.definition())
    return category

''' ===========================================================================================
FUCNTION assign_category : parse the ingredient phrase and prepare to find its category
=========================================================================================== '''
def assign_category(ele):
    # break up the ingredient phrase into list of seperate parts
    words = word_tokenize(ele)

    # filter out stop words (of, the, a, ...)
    include_stop_words = set()
    include_stop_words.add('can')
    measurements = set(["tsp", "tbsp","cup", "cups", "teaspoon", "teaspoons", "tablespoon",
                        "tablespoons", "quart", "quarts", "pint", "pints", "ounce", "ounces"])
    stop_words = set(stopwords.words('english')) - include_stop_words
    words_filtered = []
    for w in words:
        if w not in stop_words and w not in measurements:
            words_filtered.append(w)

    # remove numeric values
    reg_spec_chars = re.compile("[-!$%^&*()_+|~=`{}\[\]:;<>?,.\/]")             # find special characters
    reg_quantity = re.compile("[-]?[0-9]+[,.]?[0-9]*([\/][0-9]+[,.]?[0-9]*)*")  # find integers and fractions
    reg_parentheses = re.compile("\((.*?)\)")   # find words between parentheses
    for w in words_filtered:
        if re.search(reg_quantity, w):
            words_filtered.remove(w)        # remove numbers
        elif re.search(reg_spec_chars,w):
            words_filtered.remove(w)        # remove special characters
        elif re.search(reg_parentheses,w):
            words_filtered.remove(w)

    # create list of foods from synset
    food = wn.synset('foodstuff.n.02')
    #foods = list(set([w for s in food.closure(lambda s:s.hyponyms()) for w in s.lemma_names()]))
    foods = []
    for s in food.closure(lambda s:s.hyponyms()):
        for w in s.lemma_names():
            foods.append(w)


    found_flag = False   # which statement to print
    food_name = ''       # the name of the food found, some names are compound i.e. vanilla_extract

    # ---- build list of compound ingredients by chaining words together ---- #
    # ex: 'teaspoon vanilla extract'   ---> [teaspoon_vanilla, vanilla_extract]
    wf_compounds = []
    for i, val in enumerate(words_filtered):
        if i > 1:
            wf_compounds.append(words_filtered[i-1] + "_" + val)

    # ---- check each list item ---- #
    for f in foods:
        for c in wf_compounds:  # first check all the compound words
            if f == c:
                food_name = c
                found_flag = True
                break
        if not found_flag:      # if not found check each word alone
            for w in words_filtered:
                if f == w:
                    food_name = f
                    found_flag = True
                    break

    # let the default category be other
    category = 'Other'

    # if the word is a food, find it's category
    if food_name is not '':
        category = categorize(food_name)
    # else, assign it to Other
    else:
        # using this api is very slow which is why it is used as a back up method
        nbd_key = 'cH6ecteE92SztSSisswTdibM8u5oQsasNKYDhN77'
        ingredient_phrase = '+'.join(words_filtered)
        ndb_url = 'https://api.nal.usda.gov/ndb/search/?format=json&q='+ingredient_phrase+'&ds=Standard%20Reference&max=1&offset=0&api_key='+nbd_key
        ndb_content = requests.get(ndb_url)
        ndb_dict = json.loads(ndb_content.text)

        nbd_group = ''
        for key, value in ndb_dict.items():
            if key != 'errors':
                nbd_group = ndb_dict['list']['item'][0]['group']

        # try to categorize individual words rather than whole phrase
        if nbd_group == '':
            for w in words_filtered:
                nbd_key = 'cH6ecteE92SztSSisswTdibM8u5oQsasNKYDhN77'
                ndb_url = 'https://api.nal.usda.gov/ndb/search/?format=json&q=' + w + '&ds=Standard%20Reference&max=10&offset=0&api_key=' + nbd_key
                ndb_content = requests.get(ndb_url)
                ndb_dict = json.loads(ndb_content.text)

                for key, value in ndb_dict.items():
                    if key != 'errors':
                        nbd_group = ndb_dict['list']['item'][0]['group']

        if nbd_group == 'Dairy and Egg Products':
            category = 'Dairy/Eggs'
        elif nbd_group == 'Sausages and Luncheon Meats':
            category = 'Meat'
        elif nbd_group == 'Fruits and Fruit Juices':
            category = 'Produce'
        elif nbd_group == 'Vegetables and Vegetable Products':
            category = 'Produce'
        elif nbd_group == 'Spices and Herbs':
            category = 'Cooking/Baking'
        elif nbd_group == 'Cereal Grains and Pasta':
            category = 'Canned/Dry Goods'
        elif nbd_group == 'Legumes and Legume Products':
            category = 'Canned/Dry Goods'
        elif nbd_group == 'Soups, Sauces, and Gravies':
            category = 'Canned/Dry Goods'
        elif nbd_group == 'Sweets':
            category = 'Cooking/Baking'
        elif nbd_group == 'Fats and Oils':
            category = 'Cooking/Baking'
        elif nbd_group == 'Baked Products':
            category = 'Bakery'
        elif nbd_group == 'Poultry Products':
            category = 'Meat'
        else:
            category = 'Other'

    # pull the category from the database
    if category is None or category is 'Other':
        primary_category = Category.query.filter_by(name="Other").first()
    else:
        primary_category = Category.query.filter_by(name=category).first()

    return(primary_category.id)

''' ===========================================================================================
PAGE list : displays the selected list, form to enter url to scrape recipe web pages
=========================================================================================== '''
class Error(Exception):
   """Base class for other exceptions"""
   pass

class InvalidURLError(Error):
    """Please enter a valid URL"""
    pass

@app.route("/mylists/list/<list_id>", methods= ['GET','POST'])
def list(list_id):
    # redirect if user not logged in
    if current_user.is_authenticated == False:
        flash(f'Please login', 'info')
        return redirect(url_for('login'))

    # load list
    list_data = Grocerylist.query.filter_by(id=list_id).first()

    # To add list items in manually
    additional_item = AdditionalListItem()
    if additional_item.validate_on_submit and additional_item.submit_item.data and request.method == 'POST':
        cat_type = assign_category(additional_item.new_item.data)
        new_item = Item(name=additional_item.new_item.data, user=current_user, list_id=list_data.id, category_id=cat_type) #store
        db.session.add(new_item)
        db.session.commit()

    # To add list items with a url
    form = EnterRecipe()
    if form.validate_on_submit and form.submit.data and request.method == 'POST':
        try:
            # get url posted to form
            url = form.recipe_url.data

            # check if url is valid
            valid_url = re.compile("^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$")
            if not re.search(valid_url, url):
                raise InvalidURLError

            # some websites require headers to make a request
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

            # make request to url
            r = requests.get(url, headers = headers)

            # parse html with bs4
            soup = BeautifulSoup(r.text,'html5lib')

            # METHOD 1: parse for JSON-LD
            ld_json = soup.find("script", {"type" : "application/ld+json"})
            if ld_json is not None:
                # if recipeIngredient not found in first block of script, then search next
                failsafe = 0;
                while "recipeIngredient" not in str(ld_json) and failsafe < 10:
                    ld_json = ld_json.findNext("script", {"type": "application/ld+json"})
                    failsafe = failsafe + 1 #provide a failsafe to avoid infinite loop. This occurs if there is no more application/ld_json tags

                # parse out html tags
                ld_json = re.sub(r"<[^>]*>", "", ld_json.string)

                # get the JSON, make sure it is in correct format
                items_dict = json.loads(ld_json)
                if ld_json.startswith('[') and ld_json.endswith(']'):
                    items_dict = items_dict[1]

                # search the JSON for ingredients
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
                    item = Item(name=ele, user=current_user, list_id=list_id, recipe_id=recipe_data.id, category_id=get_category) #store
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

                recipe_list = soup.findAll(["li","span"], itemprop=re.compile("\w*([Ii]ngredient)\w*"))

                for itemprop in recipe_list:
                    get_category = assign_category(itemprop.text)
                    item = Item(name=itemprop.text, user=current_user, list_id=list_id, recipe_id=recipe_data.id, category_id=get_category) #store
                    db.session.add(item)
                    db.session.commit()

            # Success if we got to here
            flash(f'Ingredients obtained from {form.recipe_url.data}', 'success')
        except InvalidURLError:
            flash(f'Please enter a valid URL', 'danger')
        except Exception as e:
            print("EXCEPTION")
            print(e)
            flash(f'Cannot obtain ingredients from {form.recipe_url.data}', 'danger')

    # get filtered_items
    filtered_items = []
    filtered_items = Filter_Item.query.filter_by(user_id=current_user.id).all()

    # get all list items
    items = []
    items = Item.query.filter(Item.list_id==list_id).all()

    for item in items:
        for fi in filtered_items:
            if fi.name in item.name and fi.name != '':
                items.remove(item)
                break

    # get all recipes in this list
    recipes = []
    for i in items:
        find_recipe = Recipe.query.filter_by(id=i.recipe_id).first()
        if find_recipe not in recipes:
            recipes.append(find_recipe)

    # delete recipe form
    delete_recipe = DeleteRecipe()
    delete_recipe.selected_recipe.choices = recipes #populate drop-down form

    return render_template('list.html', form=form, items=items, delete_recipe=delete_recipe, list_id=list_id, list = list_data, additional_item=additional_item)

''' ===========================================================================================
PAGE delete : deletes selected recipe and reroutes back to list page
=========================================================================================== '''
@app.route("/delete", methods= ['GET','POST'])
def delete():
    recipe_id = request.form.get('recipe')
    list = request.form.get('list')
    Item.query.filter(Item.recipe_id==recipe_id).delete()
    Recipe.query.filter(Recipe.id==recipe_id).delete()

    db.session.commit()

    flash(f'Deleted recipe', 'success')
    return redirect(url_for('list', list_id=list))

''' ===========================================================================================
PAGE calendar : organizes recipes with selected times
=========================================================================================== '''
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if date is None:
        return 'None'
    format='%b %d, %Y'
    return date.strftime(format)

@app.route("/calendar", methods = ['GET','POST'])
def calendar():
    # redirect if not logged in
    if current_user.is_authenticated == False:
        flash(f'Please login', 'info')
        return redirect(url_for('login'))

    select_form = SelectRecipe()
    recipes = []
    recipes_with_dates = []
    try:
        recipes = Recipe.query.filter(User.id==current_user.id).all()
        recipes_with_dates = Recipe.query.filter(User.id==current_user.id, Recipe.plan_date != None).order_by(Recipe.plan_date.desc()).all()
    except Exception as e:
        print(e)

    if select_form.validate_on_submit and select_form.submit.data and request.method == 'POST':

        # get the time for the recipe
        recipe_datetime = request.form.get('meal-time')

        # query the recipe
        recipe_id = request.form.get('recipe')
        get_recipe = Recipe.query.filter(Recipe.id==recipe_id, Recipe.user_id==current_user.id).first()
        print(get_recipe.name)
        # modify the recipe by setting it to the chosen time
        get_recipe.plan_date = datetime.strptime(recipe_datetime, "%Y-%m-%dT%H:%M")

        # commit the changes
        db.session.commit()

        flash(f'Added recipe', 'success')
        return redirect(url_for('calendar'))

    select_form.selected_recipe.choices = recipes
    return render_template('calendar.html', select_form=select_form, recipes=recipes, recipes_with_dates=recipes_with_dates)
