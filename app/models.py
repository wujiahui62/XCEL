from app import app, db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask import redirect, url_for
from time import time
import jwt

# association table
regis = db.Table('regis',
    db.Column('user_id', db.Integer, db.ForeignKey('member.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    members = db.relationship('Member', backref='account')
    admin = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<User: {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_members(self):
        return Member.query.filter_by(account_id=self.id)

    def get_reset_password_token(self, expires_in=1800):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

# static method can be invoked from the class
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    country = db.Column(db.String(50))
    other = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(200))
    zip = db.Column(db.String(10))
    cell = db.Column(db.String(20))
    check1 = db.Column(db.Boolean, default=False)
    healthNotes = db.Column(db.String(100))
    EmergencyContact = db.Column(db.String(64))
    EmergencyPhone = db.Column(db.String(20))

    # one-to-many: User, Member
    account_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    #the registers is going to be an attribute in classs Event, even though it is declared here
    # lazy = dynamic is to define how the data is loaded, so not all data is loaded at once, it is loaded upon query
    registrations = db.relationship('Event', secondary=regis,
    # the condition that links the left side entity(user) with the association table
    # primaryjoin=(regis.c.user_id == id),
    # the condition that links the right side entity(event) with the association table
    # secondaryjoin=(regis.c.event_id == id),
    backref=db.backref('registers', lazy='dynamic'),
    lazy='dynamic')

    def __repr__(self):
        return '<Member: {} {}>'.format(self.fname, self.lname)

    def register(self, event):
        if not self.has_registered(event):
            self.registrations.append(event)
    
    def unregister(self, event):
        if self.has_registered(event):
            self.registrations.remove(event)

    def has_registered(self, event):
        return self.registrations.filter(regis.c.event_id == event.id).count() > 0

    def registered_events(self):
        return Event.query.join(
            regis, (regis.c.event_id == Event.id)).filter(
                regis.c.user_id == self.id).order_by(Event.start_date.desc())


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, index=True, default=datetime.now)
    end_date = db.Column(db.DateTime, index=True)
    title = db.Column(db.String(500))
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Event: {}>'.format(self.id)

    def get_upcoming_events(self):
        now = datetime.now()
        upcoming = Event.query.filter(Event.start_date > now).order_by(Event.start_date)
        return list(upcoming)

    def get_ongoing_events(self):
        now = datetime.now()
        ongoing = Event.query.filter(Event.start_date <= now, Event.end_date >= now).order_by(Event.start_date)
        return list(ongoing)

    def get_passed_events(self):
        now = datetime.now()
        passed = Event.query.filter(Event.end_date < now).order_by(Event.start_date.desc())
        return list(passed)

    def get_available_events(self):
        return Event.query.filter(self.end_date - datetime.now() >= 0).order_by(Event.start_date.desc())
    
    def registrable(self):
        return self.start_date >= datetime.now()

class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Member, db.session))
admin.add_view(MyModelView(Event, db.session))

