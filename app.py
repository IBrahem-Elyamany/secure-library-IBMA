from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
import check
from markupsafe import escape
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
        username = escape(request.form['username'])
        password = request.form['password']

        user = db.get_user(connection, username)
        if user:
            if check.is_password_correct(password,user[3]):
                session['username']=user[1]
                return redirect(url_for('index'))
    flash("Invalid username or password", "danger")
    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signup():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = request.form['password']
        email = escape(request.form['email'])
        lNAme=escape(request.form['lastname'])

        if not check.is_valid_email(email):
             flash("Sorry You Entered invalid email", "danger")
             return render_template('signup.html')

        if not check.is_strong_password(password):
            flash("Sorry You Entered a weak Password Please Choose a stronger one", "danger")
            return render_template('signup.html')

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
    if 'username' in session:
        if session['username']=='admin':
            if request.method=='POST':
                    photo=request.files.get('photo')
                    if not check.allowed_size(photo):
                        flash('invalid size','danger')
                        return redirect(url_for('addproduct'))
                    if not check.allowed_ex(photo.filename):
                        flash('invalid extention' ,'danger')
                        return redirect(url_for('addproduct'))
                    data={'name':escape(request.form['name']),
                        'price':escape(request.form['price']),
                        'amout':escape(request.form['amout']),
                        'photo':escape(photo.filename),
                        'text':escape(request.form['text']),
                        'type':escape(request.form['type'])}
                    photo.save(os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], photo.filename))
                    db.add_product(connection,data)
                    return redirect(url_for('addproduct'))
            return render_template('addproduct.html')
    return redirect(url_for('index'))

@app.route('/deleteproduct/<id>')
def deleteproduct(id):
    if 'username' in session:
        if session['username']=='admin':
            db.delete_product(connection,id)
            return redirect(url_for('product'))
    return redirect(url_for('index'))

@app.route('/product')
def product():
    if 'username' in session:
        if session['username']=='admin':
                return render_template('product.html',products=db.get_product(connection))
    return redirect(url_for('index'))

@app.route('/editproduct/<id>',methods=['GET','POST'])
def editproduct(id):
    if 'username' in session:
        if session['username']=='admin':
            product=db.get_product_id(connection,id)
            if request.method=="GET":
                product=db.get_product_id(connection,id)
                return render_template('editproduct.html',product=product)
            elif request.method=='POST':
                request_type=request.form.get('request_type')
                if request_type=='upload_photo':
                    photo=request.files['photo']
                    if photo:
                        if not check.allowed_size(photo):
                            flash('invalid size','danger')
                            return redirect(url_for('editproduct',id=id))
                    if not check.allowed_ex(photo.filename):
                            flash('invalid extention' ,'danger')
                            return redirect(url_for('editproduct',id=id))
                    db.update_photo_product(connection,id,photo.filename)
                    photo.save(os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], photo.filename))
                elif request_type=='update':
                    data={
                        'name':escape(request.form['name']),
                        'price':escape(request.form['price']),
                        'amout':escape(request.form['amout']),
                    'text':escape(request.form['text']),
                    'type':escape(request.form['type'])}
                    db.update_product(connection,data,product[0])
                return redirect(url_for('editproduct',id=id))
            return render_template('editproduct.html',product=product)
    return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))
@app.route('/deleteuser/<id>')
def deleteuser(id):
    if 'username' in session:
        if session['username']=='admin':
            db.delete_user(connection,id)
            return redirect(url_for('index'))
if __name__ == '__main__':
    db.init_db(connection)
    db.inittable_product(connection)
    db.seed_admin_user(connection)
    app.run(debug=True)