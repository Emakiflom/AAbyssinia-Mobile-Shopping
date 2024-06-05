from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import pyrebase
import random
import string

app = Flask('__name__')
app.secret_key = 'your_secret_key'

config = {
  "apiKey": "AIzaSyDWaWvTMA563HJpopkVDXah0m-P-iDNcM0",
  "authDomain": "absiniyamobile.firebaseapp.com",
  "projectId": "absiniyamobile",
  "storageBucket": "absiniyamobile.appspot.com",
  "databaseURL": "https://absiniyamobile.firebaseio.com",
  "messagingSenderId": "847444916101",
  "appId": "1:847444916101:web:e5d56f76242de8b4c9f6ec",
  "measurementId": "G-40BMPNTXV2"
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'absiniya'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'

mysql = MySQL(app)


def generate_random_combination():
    characters = string.ascii_lowercase
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
def home():
    # if 'username' in session:
    #     return render_template('index.html', username=session['username'])
    # else:
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM item")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"select username, password from tbl_users where username = '{username}'")
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username and password')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        unique_combination = generate_random_combination()
        detail = request.form['detail']

        upload = request.files['image']
        storage.child("images/"+unique_combination+".jpg").put(upload)

        get_pic_url = storage.child("images/"+unique_combination+".jpg").get_url(None)


        print(get_pic_url)
        cur = mysql.connection.cursor()
        cur.execute(f"insert into item(name, price, category, image, details) values ('{name}', '{price}', '{category}', '{get_pic_url}', '{detail}')")
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home'))
    
    
    return render_template('register.html')

@app.route("/view_item/<int:item_id>")
def view_item(item_id):
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return render_template("view_item.html", item=data)
    else:
        return "Item not found."


@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return render_template("edit_item.html", item=data)
    else:
        return "Item not found."



@app.route('/edit', methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        
        item_id = request.form['item_id']
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        unique_combination = generate_random_combination()
        detail = request.form['detail']
        image_url = request.form['image_url']
        
      
      
        file = request.files['image']

        if file:
            upload = request.files['image']
            storage.child("images/"+unique_combination+".jpg").put(upload)
            image_url = storage.child("images/"+unique_combination+".jpg").get_url(None)


        cur = mysql.connection.cursor()
        sql = "UPDATE item SET name = %s, price = %s, category = %s, image = %s, details = %s WHERE item_id = %s"
        val = (name, price, category, image_url, detail, item_id)

        try:
            cur.execute(sql, val)
            mysql.connection.commit()
            message = "Data updated successfully!"
        except mysql.connector.Error as err:
            message = f"Error updating data: {err}"
        
        cur.close()

        return redirect(url_for('home'))
    
    
    return render_template('edit_item.html')

@app.route("/delete_item/<int:item_id>")
def delete_item(item_id):
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return render_template("delete_item.html", item=data)
    else:
        return "Item not found."

@app.route('/delete', methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        
        item_id = request.form['item_id']
        cursor = mysql.connection.cursor()
        sql = "DELETE FROM item WHERE item_id = %s"
        val = (item_id,)
        cursor.execute(sql, val)
        mysql.connection.commit()

        return redirect(url_for('home'))
    
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)