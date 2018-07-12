import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'OiiLCJhbGceyJ0eXAiiJIUzI1JKV1QNiJ9'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = 'baixiu2014@gmail.com'
    ADMIN_ACCOUNT = 'wujiahui1987@gmail.com'
    EVENTS_PER_PAGE = 3
    MAIL_SERVER='smtp.googlemail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='libaixiu2014@gmail.com'
    MAIL_PASSWORD='cloud_app'

   