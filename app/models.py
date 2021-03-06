from app import app, db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, form
from flask import redirect, url_for
from time import time
import jwt
import os
import os.path as op
from sqlalchemy.event import listens_for
from flask_admin.form import rules
from flask_admin.contrib import sqla
from jinja2 import Markup
from os.path import join
from sqlalchemy.dialects.mysql import TIME


# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'static/files')
try:
    os.mkdir(file_path)
except OSError:
    pass

# association table
regis = db.Table('regis',
    db.Column('user_id', db.Integer, db.ForeignKey('member.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    )

# association table Event <-> File
event_file_table = db.Table('event_file_table',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'))
    )

# association table Event <-> Image
event_image_table = db.Table('event_image_table',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'))
    )

# association table League <-> Image
league_image_table = db.Table('league_image_table',
    db.Column('league_id', db.Integer, db.ForeignKey('league.id')),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'))
    )


# association table League <-> Team
# league_team_table = db.Table('league_team_table',
#     db.Column('league_id', db.Integer, db.ForeignKey('league.id')),
#     db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
#     )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    members = db.relationship('Member', backref='account')
    teams = db.relationship('Team', backref='account')
    admin = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<User: {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_members(self):
        return Member.query.filter_by(account_id=self.id)

    def get_teams(self):
        return Team.query.filter_by(account_id=self.id)

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
    weekday = db.Column(db.String(64))
    time = db.Column(db.TIME())
    start_date = db.Column(db.DateTime, index=True, default=datetime.now)
    end_date = db.Column(db.DateTime, index=True)
    registration = db.Column(db.DateTime, index=True)
    location = db.Column(db.String(128))
    limit = db.Column(db.Integer)
    participants = db.Column(db.Integer, default=0)
    title = db.Column(db.String(500))
    body = db.Column(db.Text)
    event_file = db.relationship('File', secondary=event_file_table, 
                  backref=db.backref('file_event', lazy='dynamic'), lazy='dynamic')
    event_image = db.relationship('Image', secondary=event_image_table, 
                  backref=db.backref('image_event', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):
        return '<Event: {}>'.format(self.id)

    # def get_upcoming_events(self):
    #     now = datetime.now()
    #     upcoming = Event.query.filter(Event.start_date > now).order_by(Event.start_date)
    #     return list(upcoming)

    # def get_passed_events(self):
    #     now = datetime.now()
    #     ongoing = Event.query.filter(Event.start_date <= now).order_by(Event.start_date)
    #     return list(ongoing)

    # def get_passed_events(self):
    #     now = datetime.now()
    #     passed = Event.query.filter(Event.end_date < now).order_by(Event.start_date)
    #     return list(passed)

    def get_events(self):
        events = Event.query.order_by(Event.start_date.desc())
        return list(events)

    def registrable(self):
        if self.start_date is None or self.start_date < datetime.now():
            return False
        if self.participants is None:
            self.participants = 0
        if self.limit is None:
            self.limit = 100000
            db.session.commit()
        return self.start_date >= datetime.now() and self.participants < self.limit

    def relate_to_file(self, file):
        if not self.has_relation_to(file):
            self.event_file.append(file)
    
    def unrelate_to_file(self, file):
        if self.has_relation_to(file):
            self.event_file.remove(file)

    def has_relation_to(self, file):
        return self.event_file.filter(event_file_table.c.file_id == file.id).count() > 0

    def related_files(self):
        return File.query.join(
            event_file_table, (event_file_table.c.file_id == File.id)).filter(
                event_file_table.c.event_id == self.id)

    def relate_to_image(self, image):
        if not self.has_relation_to(image):
            self.event_image.append(image)
    
    def unrelate_to_image(self, image):
        if self.has_relation_to(image):
            self.event_image.remove(image)

    def has_relation_to(self, image):
        return self.event_image.filter(event_image_table.c.image_id == image.id).count() > 0

    def related_images(self):
        return Image.query.join(
            event_image_table, (event_image_table.c.image_id == Image.id)).filter(
                event_image_table.c.event_id == self.id)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    genre = db.Column(db.String(64))
    guy_num = db.Column(db.Integer)
    girl_num = db.Column(db.Integer)
    open_registration = db.Column(db.Date)
    start_date = db.Column(db.DateTime, index=True, default=datetime.now)
    end_date = db.Column(db.DateTime, index=True)
    time_1 = db.Column(db.DateTime)
    time_2 = db.Column(db.DateTime)
    how_long = db.Column(db.Integer)
    where = db.Column(db.String(200))
    limit = db.Column(db.Integer)
    team_num = db.Column(db.Integer)
    rule = db.Column(db.Text)
    teams = db.relationship('League_Team', back_populates='league')
    # league_team = db.relationship('Team', secondary=league_team_table, 
    #               backref=db.backref('team_league', lazy='dynamic'), lazy='dynamic')
    league_image = db.relationship('Image', secondary=league_image_table, 
                  backref=db.backref('image_league', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<League: {}>'.format(self.id)
    
    def get_teams(self):
        return Team.query.join(
            League_Team, (League_Team.team_id == Team.id)).filter(
                League_Team.league_id == self.id)

    def get_upcoming_leagues(self):
        now = datetime.now()
        upcoming = League.query.filter(League.start_date > now).order_by(League.start_date)
        return list(upcoming)

    # def get_current_leagues(self):
    #     now = datetime.now()
    #     current = League.query.filter(League.start_date <= now, League.end_date >= now).order_by(League.start_date)
    #     return list(current)

    # def get_passed_leagues(self):
    #     now = datetime.now()
    #     passed = League.query.filter(League.end_date < now).order_by(League.start_date.desc())
    #     return list(passed)

    def get_leagues(self):
        leagues = League.query.order_by(League.start_date.desc())
        return list(leagues)

    def registrable(self):
        if self.start_date is None or self.start_date < datetime.now():
            return False
        if self.team_num is None:
            self.team_num = 0
        if self.limit is None:
            self.limit = 100000
            db.session.commit()
        return self.start_date >= datetime.now() and self.team_num < self.limit
 
    def relate_to_image(self, image):
        if not self.has_relation_to(image):
            self.league_image.append(image)
    
    def unrelate_to_image(self, image):
        if self.has_relation_to(image):
            self.league_image.remove(image)

    def has_relation_to(self, image):
        return self.league_image.filter(league_image_table.c.image_id == image.id).count() > 0

    def related_images(self):
        return Image.query.join(
            league_image_table, (league_image_table.c.image_id == Image.id)).filter(
                league_image_table.c.league_id == self.id)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    leagues = db.relationship('League_Team', back_populates='team')
    # one-to-many: User, Member
    account_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # def unregister(self, event):
    #     if self.has_registered(event):
    #         self.registrations.remove(event)

    def has_registered(self, league):
        return League_Team.query.filter(League_Team.league_id==league.id, League_Team.team_id==self.id).count() > 0

    def registered_leagues(self):
        return League.query.join(
            League_Team, (League_Team.league_id == League.id)).filter(
                League_Team.team_id == self.id).order_by(League.start_date.desc())

    
# association object
class League_Team(db.Model):
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    scheduling_requests = db.Column(db.Text)
    league = db.relationship('League', back_populates='teams')
    team = db.relationship('Team', back_populates='leagues')

class ContactForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200))
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip = db.Column(db.String(10))
    country = db.Column(db.String(50))
    other = db.Column(db.String(50))
    comments = db.Column(db.Text)


# delete hoods for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass
        
        # delete thumbnail
        try:
            os.remove(op.join(file_path, form.thumbgen_filename(target.path)))
        except OSError:
            pass

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

class FileView(sqla.ModelView):
    # override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'path': form.FileUploadField
    }

    # pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

class ImageView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                                                 filename=join("files/", form.thumbgen_filename(model.path))))

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Member, db.session))
admin.add_view(MyModelView(Event, db.session))
admin.add_view(MyModelView(League, db.session))
admin.add_view(MyModelView(Team, db.session))
admin.add_view(MyModelView(League_Team, db.session))
admin.add_view(MyModelView(ContactForm, db.session))
# admin.add_view(FileView(File, db.session))
admin.add_view(ImageView(Image, db.session))