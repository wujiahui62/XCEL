from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# PA does not support multi-thread
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # send_async_email(app, msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Xcel] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_confirmation_email(user, member, event):
    send_email('[Xcel] Your registration is confirmed!',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/registration_confirmation.txt',
                                         member=member, event=event),
               html_body=render_template('email/registration_confirmation.html',
                                         member=member, event=event))

                                    
                