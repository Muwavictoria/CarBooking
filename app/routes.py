from flask import render_template, request, session, redirect, url_for
from app  import app, mysql
import MySQLdb.cursors, re, os


@app.route("/")
def home():
    username = ''
    return render_template("dasboard.html")


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
    

# Adding cars
@app.route('/addproduct', methods=['POST','GET'])
def add_products():
    msg = ''
    if request.method == 'POST' and 'numberplate' in request.form and 'carname' in request.form and 'brand' in request.form and 'color' in request.form and 'description' in request.form and  'price' in request.form and 'seats' in request.form and 'image' in request.files :
        numberplate = request.form['numberplate']
        carname = request.form['carname']
        brand = request.form['brand']
        color = request.form['color']
        description = request.form['description']
        price = request.form['price']
        seats = request.form['seats']
        image = request.files['image']

        directory = 'static/img/cars'

        if not os.path.exists(directory):
                os.makedirs(directory)

        # Save the image to a directory and get the file path
        image_path = 'static/img/cars/' + image.filename
        image.save(image_path)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO car VALUES (% s, % s, % s, % s, % s, % s, % s,% s)', (numberplate, carname, brand, color, description, price, seats, image_path ))
        mysql.connection.commit()
        msg = 'You have successfully added products !'
        return redirect(url_for('getproduct'))
    return render_template('products.html')

# Getting cars
@app.route('/products', methods=['POST','GET'])
def getproduct():
    msg =""
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT `number_plate`, `car_name`, `brand`, `color`, `description`, `price`, `seats`, `image` FROM `car`')
        car = cursor.fetchall()  # Fetch all rows from the result set
        cursor.close()
        msg = 'You have successfully got products !'

        return render_template('products.html', msg=msg, car=car)

    return render_template('products.html', car=car, msg=msg)




@app.route('/delete/<string:number_plate>', methods = ['GET','POST','DELETE'])
def delete_products(number_plate):
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM `car` WHERE number_plate=%s', (number_plate,))
    mysql.connection.commit()
    cursor.close()
    msg = 'You successfully deleted the car'

    return redirect(url_for('getproduct'))
    



@app.route('/update/<string:number_plate>', methods=['GET', 'POST'])
def update_car(number_plate):
    if request.method == 'POST':
        new_carname = request.form.get('new_carname')
        new_brand = request.form.get('new_brand')
        new_color = request.form.get('new_color')
        new_description = request.form.get('new_description')
        new_price = request.form.get('new_price')
        new_seats = request.form.get('new_seats')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE car SET car_name=%s, brand=%s, color=%s, description=%s, price=%s, seats=%s WHERE number_plate=%s",
                       (new_carname, new_brand, new_color, new_description, new_price, new_seats, number_plate))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('getproduct'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM car WHERE number_plate = %s", (number_plate,))
    car = cursor.fetchone()
    cursor.close()

    return render_template('products.html', car=car)
