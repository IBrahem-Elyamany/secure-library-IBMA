from flask import Flask, render_template, request, redirect, url_for, session, flash ,abort
import db
import os
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

#part WAF to protect (SQL injection and XSS)
def is_malicious_request(req):
    malicious_patterns = ["SELECT", "DROP", "<script>", "UNION", "--"]
    for pattern in malicious_patterns:
        if pattern in req.data.decode('utf-8').upper() or pattern in req.query_string.decode('utf-8').upper():
            return True
    return False

@app.before_request
def check_request():
    if is_malicious_request(request):
        abort(403)  


@app.route('/')
def index():
    if 'username' in session:
        if session['username']=='admin':
            return render_template('admin.html',users=db.get_all_users(connection))
        else:
            user=db.get_user(connection,session['username'])
            return render_template('index.html',products=db.get_product(connection),user=user)
    user=None
    return render_template('index.html',products=db.get_product(connection),user=user)






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
            else:
                flash("Invalid username or password", "danger")
        else :
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

@app.route('/detils/<id>', methods=['GET', 'POST'])
def detils(id):
    idd = db.get_product_id(connection, id)
    comments = db.get_comments_for_product(connection, idd[0])
    if 'username' not in session:
        user=None
        return render_template('detils.html', id=idd, comments=comments,user=user)
    user = db.get_user(connection, session['username'])
    if request.method == 'POST':
        comment = escape(request.form['comment'])
        db.add_comment(connection, idd[0], user[0], comment)
        return redirect(url_for('detils', id=id))
    return render_template('detils.html', id=idd, comments=comments,user=user)


@app.route('/add_to_cart/<id0>')
def add_to_cart(id0):
    product = db.get_product_id(connection,id0)

    
    if 'username' not in session:
        flash("You must be logged in to add items to your cart.", "warning")
        return redirect(url_for('signin'))

    
    cart = session.get('cart', [])
    cart.append({'product_id': product[0], 'prodcut_name': product[1], 'price': product[3], 'quantity': 1})
    session['cart'] = cart

    flash(f"Added product {product[0]} with price {product[3]} to your cart.", "success")
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    
    if 'username' not in session:
        flash("You must be logged in to add items to your cart.", "warning")
        return redirect(url_for('signin'))
    
    return render_template('cart.html', cart=cart)


@app.route('/checkout')
def checkout():
    if 'username' not in session:
        return redirect(url_for('index'))
    product_id = request.args.get('product_id')
    name = request.args.get('name')
    price = request.args.get('price')
    product=db.get_product_id(connection,product_id)
    session['Correct_MAC'] = check.create_mac(product[3])
    return render_template('checkout.html', product_id=product_id, name=name, price=price)

@app.route('/confirm_purchase', methods=['POST'])
def confirm_purchase():
    if 'username' not in session:
        return redirect(url_for('index'))
    product_id = request.form['product_id']
    price = request.form['price']
    product=db.get_product_id(connection,product_id)
    username=session['username']
    user=db.get_user(connection,username)
    Possible_Correct_MAC = check.create_mac(price)
    if 'Correct_MAC' in session and session['Correct_MAC'] == Possible_Correct_MAC:
        money=int(user[7])-int(price)
        if money>=0:
            flash(f"Purchase confirmed at price ${price}.",'success')
            db.update_wallet(connection,user[0],money)
            db.update_amount(connection,product[0],int(product[2])-1)
            return redirect(url_for('index'))
        else:
            flash("Sorry there is not enough Money",'danger')
            return redirect(url_for('index'))
    else:
        flash ("Purchase Failed, Please Try Again","danger")
        return redirect(url_for('index'))
@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('index'))
    session.pop('username',None)
    return redirect(url_for('index'))
@app.route('/deleteuser/<id>')
def deleteuser(id):
    if 'username' in session:
        if session['username']=='admin':
            db.delete_user(connection,id)
            return redirect(url_for('index'))
        return redirect(url_for('index'))
    return redirect(url_for('index'))



@app.route('/addtowallet/<id>',methods=['GET','POST'])
def addtowallet(id):
    if 'username' in session:
        if session['username']=='admin':
            user=db.get_user_id(connection,id)
            if request.method=="POST":
                money=request.form['wallet']
                money0=int(money)+user[7]
                db.update_wallet(connection,id,money0)
                return redirect(url_for('index'))
            return render_template('addtowallet.html',user=user)
    return redirect(url_for('index'))

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        search=escape(request.form['search'])
        products=db.get_product_search(connection,search)
        
        if 'username' in session:
            user=db.get_user(connection,session['username'])
            return render_template('index.html',products=products,user=user)
        else:
            user=None
            return render_template('index.html',products=products,user=user)



if __name__ == '__main__':
    db.init_db(connection)
    db.inittable_product(connection)
    db.seed_admin_user(connection)
    db.init_comments_table(connection)
    app.run(debug=True)