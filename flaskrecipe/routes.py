from flask import render_template, url_for, flash, redirect, request, session
from flaskrecipe.forms import RegistrationForm, LoginForm, NewListForm, EnterRecipe
from flaskrecipe.models import User, Item, List
from flaskrecipe import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import requests
import json
import re

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
MY LISTS PAGE / RECIPE PAGE
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
    try:
        lists = List.query.filter_by(user_id=current_user.id).all()
    except:
        lists = []
        flash(f'No lists have been created yet.', 'info')
    return render_template('mylists.html', lists=lists)

@app.route("/mylists/list/<list_id>", methods= ['GET','POST'])
def list(list_id):
    if current_user.is_authenticated == False:
        flash(f'Please login', 'info')
        return redirect(url_for('login'))

    # load list
    list_data = List.query.filter_by(id=list_id).first()

    form = EnterRecipe()

    # BEGIN RECIPE WEB SCRAPING
    if form.validate_on_submit and request.method == 'POST':
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

                # pull each item from dictionary
                for ele in recipe_list:
                    item = Item(name=ele, user=current_user, list_id=list_id) #store
                    db.session.add(item)
                    db.session.commit()
            else:
                oembed_json = soup.find("link", rel="alternate", type="application/json+oembed", href=True)['href'] # METHOD 2: parse for JSON-OEMBED
                api_request = requests.get(oembed_json)
                api_contents = api_request.json()
                api_contents_title = api_contents['title']
                api_contents_html = api_contents['html']
                api_soup = BeautifulSoup(api_contents_html, 'html5lib')

                recipe_list = api_soup.findAll("li", itemprop="recipeIngredient")
                for ele in recipe_list:
                    Item(name=ele, user=current_user) #store
                    db.session.add(item)
                    db.session.commit()

            # Success if we got to here
            flash(f'Ingredients obtained from {form.recipe_url.data}', 'success')
        except Exception as e:
            print(e)
            flash(f'Cannot obtain ingredients from {form.recipe_url.data}', 'danger')

    items = []
    items = Item.query.filter_by(list_id=list_id).all()

    return render_template('list.html', form=form, items=items)

    # END RECIPE WEB SCRAPING
