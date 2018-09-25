from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditUserForm, EventRegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, LeagueRegistrationForm, ContactUsForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Member, Event, Image, File, League, Team, League_Team, ContactForm
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_confirmation_email, send_account_registration_email, send_contact_us_email

first_name = None
last_name = None

@app.route('/')
@app.route('/index')
def index():
    slides = []
    # event = Event().query.filter_by(title='index').first()
    index_images = Image().query.filter_by(name='index').all()
    for image in index_images:
        slides.append(image)
    leagues = League().get_leagues()
    if len(leagues) >= 3:
        leagues = leagues[:3]
    events = Event().get_events()
    if len(events) >= 3:
        events = events[:3]
    activities = []
    return render_template("index.html", title="Home page", slide=slides[0], slides=slides[1:], len=len(slides),
    leagues=leagues, events=events, activities=activities)

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
       send_account_registration_email(user)
       flash('Congratulations! You are now a registerd user')
       return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EditUserForm()
    user = User.query.filter_by(email=username).first_or_404()
    members = Member.query.filter_by(account_id=user.id)
    count = members.count()
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
    return render_template('user.html', user=user, members=members, form=form, count=count)

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

@app.route('/my_activities')
@login_required
def my_activities():
    members = Member.query.filter_by(account_id=current_user.id)
    page = request.args.get('page', 1, type=int)
    array = []
    for member in members:
        eventobj = {}
        eventobj['member'] = member
        eventobj['events'] = member.registered_events().paginate(page, app.config['EVENTS_PER_PAGE'], False).items
        array.append(eventobj)
    return render_template('my_activities.html', array=array)

@app.route('/my_leagues')
@login_required
def my_leagues():
    teams = Team.query.filter_by(account_id=current_user.id)
    page = request.args.get('page', 1, type=int)
    array = []
    for team in teams:
        leagueobj = {}
        leagueobj['team'] = team
        leagueobj['leagues'] = team.registered_leagues().paginate(page, app.config['EVENTS_PER_PAGE'], False).items
        array.append(leagueobj)
    return render_template('my_leagues.html', array=array)

@app.route('/youth_activities')
def youth_activity():
    events = Event().get_events()
    length = len(events)
    return render_template('events.html', title='youth activities', events=events, length=length)

@app.route('/youth_activities/<event>')
def event(event):
    event = Event.query.filter_by(id=int(event)).first()
    registrable = event.registrable()
    image = event.related_images().first()
    return render_template('event_detail.html', title='event_detail', event=event, registrable=registrable, image=image)

@app.route('/youth_registrations/<event>', methods=['GET', 'POST'])
@login_required
def register_event(event):
    form = EventRegistrationForm()
    members = current_user.get_members()
    event = Event.query.filter_by(id=int(event)).first()
    form.members.choices = [(member.id, "{} {}".format(member.fname, member.lname)) for member in members]
    if request.method == 'POST':
        member_id = form.members.data
        member = Member.query.filter_by(id=member_id).first()
        if member.has_registered(event):
            flash('The member has already registered the event!')
            return redirect(url_for('index'))
        elif event.registrable():
            member.register(event)
            event.participants = event.participants + 1
            db.session.commit()
            send_confirmation_email(current_user, member, event)
            flash('The member has successfully registered the event!')
            return redirect(url_for('index'))
        else:
            flash('There registration is up to limit, contact us for further info!')
            return redirect(url_for('index'))
    return render_template('event_register.html', form=form)

@app.route('/rest_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/leagues')
def leagues():
    leagues = League().get_leagues()
    return render_template('leagues.html', title='Leagues', leagues=leagues)

@app.route('/league_registrations')
def league_registration():
    upcoming = League().get_upcoming_leagues()
    length = len(upcoming)
    return render_template('upcoming_leagues.html', title='upcoming activities', upcoming=upcoming, length=length)

@app.route('/volunteer')
def volunteer():
    return render_template('volunteer.html')

@app.route('/leagues/<league>')
def league(league):
    league = League.query.filter_by(id=int(league)).first()
    registrable = league.registrable()
    image = league.related_images().first()
    teams = league.get_teams()
    return render_template('league_detail.html', title='league_detail', league=league, registrable=registrable, image=image, teams=teams)

@app.route('/register_league/<league>', methods=['GET', 'POST'])
@login_required
def register_league(league):
    form = LeagueRegistrationForm()
    league = League.query.filter_by(id=int(league)).first()
    teams = current_user.get_teams()
    if teams is not None:
        form.teams.choices = [(team.id, "{}".format(team.name)) for team in teams]
    if request.method == 'POST':
        if form.new_team.data:
            # create a new team
            team = Team.query.filter_by(name=form.new_team.data).first()
            if team is not None and team.account_id == current_user.id:
                flash('The team already exists, please select the team in the menu or create a team with another name!')
                return redirect(url_for('register_league', league=league.id))
            else:
                team = Team(name=form.new_team.data, account=current_user)
                db.session.add(team)
        else:
            team_id = form.teams.data
            team = Team.query.filter_by(id=team_id).first()
        if team.has_registered(league):
            flash('The team has already registered the league!')
            return redirect(url_for('index'))
        elif league.registrable():
            league_team = League_Team(league_id=league.id, team_id=team.id, scheduling_requests=form.scheduling_requests.data)
            league.team_num = league.team_num + 1
            league_team.league = league
            league_team.team = team
            db.session.add(league_team)
            db.session.commit()
            send_confirmation_email(current_user, team, league)
            flash('The member has successfully registered the event!')
            return redirect(url_for('index'))
        else:
            flash('There registration is up to limit, contact us for further info!')
            return redirect(url_for('index'))
    return render_template('league_register.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactUsForm()
    if form.validate_on_submit():
        contact = ContactForm()
        contact.subject = form.subject.data
        contact.firstName = form.firstName.data
        contact.lastName = form.lastName.data
        contact.email = form.email.data
        contact.phone = form.phone.data
        contact.address = form.address.data
        contact.city = form.city.data
        contact.state = form.state.data
        contact.zip = form.zip.data
        contact.country = form.country.data
        contact.other = form.other.data
        contact.comments = form.comments.data
        db.session.add(contact)
        db.session.commit()
        send_contact_us_email(contact)
        flash('Your info is sent!')
        return redirect(url_for('index'))
    return render_template('contact.html', form=form)
