from flask import render_template, request, session, redirect, url_for
from app  import app, mysql
import MySQLdb.cursors, re


@app.route("/")
def home():
    username = ''
    return render_template("index.html", username=username)


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account: 
            session['loggedin'] = True
            session['id'] = account['admin_id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return  redirect(url_for('home'))
        else:
            msg = 'Incorrect username / password !'

    return render_template("login.html", msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO admin VALUES (NULL, % s, % s, % s)', (username, email, password ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template("register.html", msg = msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('admin_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
    

@app.route("/registerLogin")
def registerlogin():
    return render_template("loginRegister.html")




