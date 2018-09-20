from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, EnterRecipe
app = Flask(__name__)

# need to make variable later
app.config['SECRET_KEY'] = '2f2e185f6d5fe7a2e4edbd8db2c42c45'

# testing data


@app.route("/")
@app.route("/home")
def home():
    form = EnterRecipe()

    return render_template('home.html', form=form)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/signup", methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Welcome {form.username.data}', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)

@app.route("/login", methods = ['GET','POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
