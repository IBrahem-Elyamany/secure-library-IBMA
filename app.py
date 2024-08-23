from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
connection = db.connect_to_database()
app.secret_key = "IBMA"
limiter = Limiter(app=app, key_func=get_remote_address,default_limits=["50 per minute"], storage_uri="memory://")

@app.route('/signin', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signin():
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


if __name__ == '__main__':
    db.init_db(connection)
    app.run(debug=True)