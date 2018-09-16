from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

# need to make variable later
app.config['SECRET_KEY'] = '2f2e185f6d5fe7a2e4edbd8db2c42c45'

# testing data
posts = [
    {
        'author' : 'Valerie',
        'title' : 'Post 1',
        'content' : 'First content',
        'date' : '2018'
    },
    {
        'author' : 'Bob',
        'title' : 'Post 2',
        'content' : 'more content',
        'date' : '2018'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/signup")
def register():
    form = RegistrationForm()
    return render_template('signup.html', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
