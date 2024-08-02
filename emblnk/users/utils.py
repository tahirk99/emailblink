import secrets
import os
from PIL import Image
from flask_mail import Message
from flask import url_for, current_app, redirect
from emblnk import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def send_mail(email, token):
    msg = Message('Reset Password', sender='digiholixagency@gmail.com', recipients=[email])
    msg.body = f"""To reset your password please visit the below url \n\n
Password Reset link: {url_for('users.reset_password', token=token, _external=True)}\n\n
If you did not request it simply ignore.\n\nThanks,\nTeam Emblnk"""
    mail.send(msg)