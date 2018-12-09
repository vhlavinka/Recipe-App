**** GETTING STARTED ****

Install the following:

------------------------------------------------------------
Flask/Sqlalchemy - The framework used for the web app
------------------------------------------------------------
pip install flask
pip install flask_sqlalchemy
pip install flask_login
pip install flask_wtf
pip install flask_bcrypt
pip install wtforms_sqlalchemy

------------------------------------------------------------
BeautifulSoup, Requests, html5lib - Used to gather and parse ingredients
------------------------------------------------------------
pip install bs4
pip install requests
pip install html5lib


------------------------------------------------------------
nltk
------------------------------------------------------------
pip install nltk


------------------------------------------------------------
other
------------------------------------------------------------
pip install python-dateutil


**** SETTING UP THE DATABASE ****
You can reset the database by deleting the recipeapp.db file
and then running CreateTables.py

**** STARTING THE APP ****
To start the app, navigate to the directory containing the run.py file.
From the console, run:
python run.py
