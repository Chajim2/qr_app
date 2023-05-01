from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth',__name__)

@auth.route('/login', methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        fname = request.form.get('fname')
        password = request.form.get('password')
        check_password = User.query.filter_by(fname = fname).first()
        if check_password:
            if check_password_hash(check_password.password, password):
                flash('logged in', category='succes')
                login_user(check_password,remember = True)
                return redirect(url_for('views.home'))
            else:
                flash('wrong password', category='error')
        else: flash('person not found', category='error')

    return render_template("login.html", user = current_user)

@auth.route('/log_out')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign_up', methods = ["GET", "POST"])
def sign_up():
    data = request.form
    if request.method == "POST":
        check_existing = User.query.filter_by(fname = data.get('fname')).first()
        if check_existing: 
            flash('already exists', category='error')
        elif len(data.get('password1')) < 6: 
            flash("too short password", category="error")
        elif str(data.get("password1")) != str(data.get("password2")): 
            flash("passwords do not match", category="error")
        elif len(data.get("fname")) > 2 and len(data.get("lname")) > 2: 
            new_usr = User(fname = data.get("fname"),lname = data.get('lname'), password = generate_password_hash(data.get("password1")))
            db.session.add(new_usr)
            db.session.commit()

            login_user(new_usr, remember = True)

            flash("singed_in",category="succes")
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user = current_user)