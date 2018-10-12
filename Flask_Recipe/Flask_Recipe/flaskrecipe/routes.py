from flask import render_template, url_for, flash, redirect, request
from flaskrecipe.forms import RegistrationForm, LoginForm, EnterRecipe
from flaskrecipe.models import User, Item
from flaskrecipe import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import requests
import json
import re


@app.route("/", methods= ['GET','POST'])
@app.route("/home", methods= ['GET','POST'])
def home():
    form = EnterRecipe()
    posts = Item.query.all()
    return render_template('home.html', form=form, posts=posts)

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
        flash(f'Your account has been created. {form.username.data}', 'success')
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

@app.route("/list", methods = ['GET', 'POST'])
def list(url):
    # need to provide headers since some sites require for GET requests
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # send get request
    r = requests.get(url, headers = headers)

    # html of recipe page
    soup = BeautifulSoup(r.text,'html5lib')

    # store title of recipe
    title = soup.title.string

    # parse for JSON-LD
    getJSON = soup.find("script", {"type" : "application/ld+json"})

    if getJSON is not None:
        # if recipeIngredient not found in first block of script, then search next
        failsafe = 0;
        while "recipeIngredient" not in str(getJSON) and failsafe < 10:
            getJSON = getJSON.findNext("script", {"type": "application/ld+json"})
            failsafe = failsafe + 1 #provide a failsafe to avoid infinite loop. This occurs if there is no more application/ld_json tags

        # parse out tags
        getJSON = re.sub(r"<[^>]*>", "", getJSON.string)

        # create list
        list = getJSON

        # decode JSON
        list = json.loads(list)

        # extract recipe ingredient list
        recipeList = list["recipeIngredient"]

        # pull each item from dictionary
        for ele in recipeList:
            item = Item(name=ele, user=current_user) #store
            db.session.add(item)
            db.session.commit()

    # use this method if no application/ld+json
    oEmbedURL = soup.find("link", rel="alternate", type="application/json+oembed", href = True)['href']

    if getJSON is None and oEmbedURL is not None:

        apiRequest = requests.get(oEmbedURL)
        apiContents = apiRequest.json()
        apiContentsTitle = apiContents['title']
        apiContentsHtml = apiContents['html']
        apiSoup = BeautifulSoup(apiContentsHtml, 'html5lib')

        list = apiSoup.findAll("li", itemprop="recipeIngredient")

        for ele in list:
            Item(name=ele, user=current_user) #store
            db.session.add(item)
            db.session.commit()

        return render_template('home.html', form=form)
