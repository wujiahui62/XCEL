from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditUserForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Member, Event
from werkzeug.urls import url_parse

first_name = None
last_name = None

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

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EditUserForm()
    user = User.query.filter_by(email=username).first_or_404()
    members = Member.query.filter_by(account_id=user.id)
    if form.validate_on_submit():
        member = request.form.get('member')
        if member is not None:
            global first_name
            global last_name
            first_name, last_name = member.split(" ")
            if form.edit.data:
                return redirect(url_for('edit_profile'))
            elif form.delete.data:
                member = Member.query.filter_by(fname=first_name, lname=last_name, account=current_user).first()
                db.session.delete(member)
                db.session.commit()
                first_name = None
                last_name = None
                flash('The member was deleted!')
                return redirect(url_for('index'))
    return render_template('user.html', user=user, members=members, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    global first_name
    global last_name
    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        # update record
        if first_name is not None:
            member = Member.query.filter_by(fname=first_name, lname=last_name).first()
            member.fname = fname
            member.lname = lname
            member.gender = form.gender.data
            member.birthday = form.birthday.data
            member.country = form.country.data
            member.other = form.other.data
            member.state = form.state.data
            member.city = form.city.data
            member.address = form.address.data
            member.zip = form.zip.data
            member.cell = form.cell.data
            member.healthNotes = form.healthNotes.data
            member.EmergencyContact = form.emergencyContact.data
            member.EmergencyPhone = form.emergencyPhone.data
            first_name = None
            last_name = None
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('index'))
    elif request.method == 'GET':
        member = Member.query.filter_by(fname=first_name, lname=last_name).first()
        form.fname.data = first_name
        form.lname.data = last_name
        if member is not None:
            form.gender.data = member.gender
            form.birthday.data = member.birthday
            form.country.data = member.country
            form.other.data = member.other
            form.state.data = member.state
            form.city.data = member.city
            form.address.data = member.address
            form.zip.data = member.zip
            form.cell.data = member.cell
            form.healthNotes.data = member.healthNotes
            form.emergencyContact.data = member.EmergencyContact
            form.emergencyPhone.data = member.EmergencyPhone

    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    form = EditProfileForm()
    if form.validate_on_submit():
        members = current_user.get_members()
        fname = form.fname.data
        lname = form.lname.data
        for member in members:
            if member.fname == fname and member.lname == lname:
                flash('Member with the same name already exists!')
                return redirect(url_for('add_member'))
        new_member = Member(fname=fname, lname=lname, account=current_user)
        new_member.gender = form.gender.data
        new_member.birthday = form.birthday.data
        new_member.country = form.country.data
        new_member.other = form.other.data
        new_member.state = form.state.data
        new_member.city = form.city.data
        new_member.address = form.address.data
        new_member.zip = form.zip.data
        new_member.cell = form.cell.data
        new_member.healthNotes = form.healthNotes.data
        new_member.EmergencyContact = form.emergencyContact.data
        new_member.EmergencyPhone = form.emergencyPhone.data
        db.session.add(new_member)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    return render_template('edit_profile.html', title='Add Member', form=form)


@app.route('/delete_member')
@login_required
def delete_member(member):
    global first_name
    global last_name
    if first_name is not None:
        member = Member.query.filter_by(fname=first_name, lname=last_name).first()
        db.session.delete(member)
        db.session.commit()
        return redirect(url_for('index'))
