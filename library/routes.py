from ast import Not
from distutils.log import info
import re
from unicodedata import category, name
from library import app
from flask import flash, render_template, redirect, url_for, flash, get_flashed_messages, request
from library.models import Item, User
from library.form import RegisterForm, LoginForm, PurchaseItemForm
from library import db
from flask_login import current_user, login_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home_page(): 
    return render_template('home.html')

@app.route('/browse', methods=['GET','POST'])
@login_required
def browse_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        purchased_item = request.form.get("purchased_item")
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.owner = current_user.id
                current_user.budget -= p_item_object.price
                db.session.commit()
                flash(f'{p_item_object.name} is purchased for {p_item_object.price}',category='success')
            else:
                flash("Insufficient Funds", category='danger')
        return redirect(url_for('browse_page'))
    items = Item.query.all()
    owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('browse.html', items=items, purchase_form=purchase_form, owned_items=owned_items )

@app.route('/my_books')
def my_books_page():
    owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('my_books.html', owned_items=owned_items)
 
@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        db.session.add( user_to_create )
        db.session.commit()
        login_user(user_to_create) 
        flash(f'Success! You are logged in as : {user_to_create.username}',category='success')

        return redirect(url_for('browse_page'))
    if form.errors!={}:
        for err_msg in form.errors.values():
            flash(f'there is an error creating the user : {err_msg}',category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm() 
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as : {attempted_user.username}',category='success')
            return redirect(url_for('browse_page'))
        else:
            flash('Username and password are not matched',category='danger')
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out', category='info')
    return redirect(url_for('home_page'))
