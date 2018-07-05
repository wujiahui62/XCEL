from app import app, db, login
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask import redirect, url_for

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


class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.String(200))
    zip = db.Column(db.String(10))
    cell = db.Column(db.String(20))
    check1 = db.Column(db.Boolean, default=False)
    healthNotes = db.Column(db.String(100))
    EmergencyContact = db.Column(db.String(64))
    EmergencyPhone = db.Column(db.String(20))

    #the registers is going to be an attribute in classs Event, even though it is declared here
    # lazy = dynamic is to define how the data is loaded, so not all data is loaded at once, it is loaded upon query
    registrations = db.relationship('Event', secondary=regis, backref=db.backref('registers', lazy='dynamic'))
    # one-to-many: User, Member
    account_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Member: {} {}>'.format(self.fname, self.lname)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date)
    title = db.Column(db.String(500))
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Event: {}>'.format(self.title)

class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# class MyAdminIndexView(AdminIndexView):
#     def is_accessible(self):
        # if current_user.is_authenticated:
        #     return current_user.admin
        # return False

#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('login'))

# admin = Admin(app, index_view=MyAdminIndexView)
admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Member, db.session))
admin.add_view(MyModelView(Event, db.session))
# admin.add_view(MyModelView(regis, db.session))


#event1.register.append(user1)
#db.session.commit()
# account = User.query.filter_by(email=current_user.email).first()
# create a new member: x = Member(fname=Evan, lname=li, account=account)
# db.session.add(x), db.session.commit()

