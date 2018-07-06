from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Member
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title="Home page")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        #if there is no next page or next page is not a relative path
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
       user = User(email=form.email.data)
       user.set_password(form.password.data)
       db.session.add(user)
       db.session.commit()
       flash('Congratulations! You are now a registerd user')
       return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(email=username).first_or_404()
    members = Member.query.filter_by(account_id=user.id)
    member = request.form.get('member')
    return render_template('user.html', user=user, members=members)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # form = EditProfileForm()
    member = request.form.get('member')
    print(member)
    # fname, lname = member.split(" ")
    # print(fname)
    # form.fname.data = fname
    # form.lname.data = lname
    # if form.validate_on_submit():
    #     print('post')
    #     current_user.fname = form.fname.data
    #     db.session.commit()
    return redirect(url_for('index'))
    # return render_template('edit_profile.html', title='Edit Profile', form=form)
