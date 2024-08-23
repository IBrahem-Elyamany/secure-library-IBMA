from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.config['UPLOAD_FOLDER_PRODUCTS'] = 'static/uploads/products/'
connection = db.connect_to_database()
app.secret_key = "IBMA"
limiter = Limiter(app=app, key_func=get_remote_address,default_limits=["50 per minute"], storage_uri="memory://")

@app.route('/')
def index():
    if 'username' in session:
        if session['username']=='admin':
            return render_template('admin.html',users=db.get_all_users(connection))
        else:
            return render_template('users.html',products=db.get_product(connection),username=session['username'])

    return render_template('index.html',products=db.get_product(connection))



@app.route('/signin', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.get_user(connection, username)
        if user:
            if user[3]==password:
                session['username']=user[1]
                flash("Username already exists. Please choose a different username.", "danger")
                return redirect(url_for('index'))
        else:
            
            return redirect(url_for('signin'))
    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        lNAme=request.form['lastname']

        # if not utils.is_strong_password(password):
        #     flash(
        #         "Sorry You Entered a weak Password Please Choose a stronger one", "danger")
        #     return render_template('signup.html')

        user = db.get_user(connection, username)
        if user:
            flash("Username already exists. Please choose a different username.", "danger")
            return redirect(url_for('signup'))
        else:
            db.add_user(connection ,username ,email ,lNAme , password , "images.png")
            return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/addproduct',methods=['GET','POST'])
def addproduct():
    if request.method=='POST':
        photo=request.files.get('photo')
        
        data={'name':request.form['name'],'price':request.form['price'],'amout':request.form['amout'],'photo':photo.filename,
            'text':request.form['text'],'type':request.form['type']}
        photo.save(os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], photo.filename))
        db.add_product(connection,data)
        return redirect(url_for('addproduct'))
    return render_template('add_product.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.init_db(connection)
    db.inittable_product(connection)
    db.seed_admin_user(connection)
    app.run(debug=True)