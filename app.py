#
# File: app.py
# Author: Daniel Oliveira
#

### Flask app to connect user interface and the chatbot ###

## Import dependencies ##

import os
import re
import bcrypt
import MySQLdb.cursors
from dotenv import load_dotenv
from flask import *
from flask_mysqldb import MySQL
from chatbot import *

load_dotenv()

# Initialize Flask App #

app = Flask(__name__)

app.secret_key = os.environ['SECRET_KEY']

# Database Connection Details #

app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']

# Intialize MySQL #

mysql = MySQL(app)

## Login Request Mapping ##

@app.route('/crexusers/', methods=['GET', 'POST'])
def login():

    msg = ''

    # Check if user exists and matches password on database, when request by the user #

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        # Verify bcrypt hash; reject if user not found or password doesn't match #

        if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['name'] = account['name']
            session['balance'] = account['balance']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'            # If account doesn´t exist #

    return render_template('site.html', msg=msg)

## Logout Request Mapping ##

@app.route('/crexusers/logout')
def logout():

    # Remove account data, log out and redirect to login page#

   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('name', None)
   session.pop('balance', None)

   return redirect(url_for('login'))

## Register Request Mapping ##

@app.route('/crexusers/register', methods=['GET', 'POST'])
def register():

    msg = ''

    # Confirm if all user data doesn't exist in the database #

    if request.method == 'POST' and 'username' in request.form and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not name:
            msg = 'Please fill out the form!'

        # If all the data is correct and isn't registered on database, create new user #

        else:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (username, name, password_hash, email, 0,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    # Handle incorrect forms #

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)

## Home Page Mapping ##

@app.route('/crexusers/home', methods=['GET', 'POST'])
def home():

    # Get User BTC Balance and render homepage #

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT balance FROM accounts WHERE name = %s' , (session['name'],))
    balance = cursor.fetchone()
    balance = int(balance['balance'])

    if 'loggedin' in session:
        return render_template('home.html', name=session['name'], balance=balance)

    return redirect(url_for('login'))

## Connection between User Interface and Chatbot ##

@app.post("/crexusers/predict")
def predict():

    # Get Chatbot answer to User Question, and return it#

    text = request.get_json().get("message")
    response = communicate(text, id=session['id'], name=session['name'])
    message = {"answer": response}

    return jsonify(message)

## Run file directly on http://localhost:5000/crexusers/ ##

if __name__ == "__main__":
    app.run(debug=True)
