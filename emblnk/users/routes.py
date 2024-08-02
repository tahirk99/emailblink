from flask import Blueprint, url_for, redirect, render_template, flash, request, session, jsonify
from emblnk.users.utils import save_picture, send_mail
from flask_login import login_user, current_user, logout_user, login_required
from emblnk.users.forms import (RegisterationForm, LoginForm, UpdateProfileForm, 
                                ConfigurationForm, RequestResetForm, ResetPasswordForm)
from emblnk import db, bcrypt
from emblnk.models import User, Senders
from emblnk.campaigns.MailSender import send_test_email, test_mail

users = Blueprint('users', __name__)

@users.route('/error', methods=['GET', 'POST'])
def custom_error():
    print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'GET':
        return render_template('errors/custom_error.html', error=session.get('error'))
    elif request.method == 'POST':
        session.pop('error', None)
        referer = request.referrer
        return redirect(referer) if not '/error' in referer else redirect('/')

@users.route('/register/', methods=['GET', 'POST'])
def register():
    print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=str(form.username.data).lower(), email=form.email.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! Now you can login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)

# @login_required
@users.route("/lg")
def lg():
    from flask import session
    # To clear session data
    session.clear()
    from flask_caching import Cache
    # Assuming you've already initialized cache in your Flask app
    cache = Cache()
    # To clear the entire cache
    #cache.clear()
    print("----CLEARED---------")
    u = current_user
    print("________LG_____", u)
    return f"Hello {u}"


@users.route('/login/', methods=["GET", "POST"])
def login():
    print(current_user)
    form = LoginForm()
    if form.validate_on_submit():
        login_creds = User.query.filter_by(email=form.email.data).first()
        if login_creds and bcrypt.check_password_hash(login_creds.password, form.password.data):
            print("-----------PASSED---------")
            try:
                login_user(user=login_creds, force=True)
                flash(f'Welcome back', 'success')
                print("-----------PASSED2222---------")
                return redirect("/")
            except Exception as e:
                print("Error loggin in", e)
        else:
            flash(f'Login unsuccesful please check email and password', 'danger')
    return render_template('users/login.html', title='Login', form=form)

@users.route('/logout/')
def logout():
    logout_user()
    if current_user.is_authenticated:
        flash(f'Logged out..!', 'success')
        return redirect(url_for('users.login'))
    else:
        return redirect(url_for('users.login'))

@users.route('/settings/account/', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        print(form.data)
        if form.username.data != '':
            current_user.username = str(form.username.data).lower()
        if form.email.data != '':
            current_user.email = form.email.data
        if form.bio.data != '':
            current_user.bio = form.bio.data
        if form.picture.data != None:
            current_user.image_file = save_picture(form.picture.data)
        current_user.hide_email = form.show_email.data
        if form.username.data == '' and form.email.data == '':
            pass
        else:
            db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/'+current_user.image_file)
    return render_template('users/account.html', active_page='settings',active_settings_page='account', image_file=image_file, form=form)

@users.route("/reset-password/", methods=['GET', 'POST'])
def password_reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.get_password_reset_token()
        send_mail(user.email, token)
        flash('An email has been sent to your id with instructions', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/password_reset_request.html', title='Reset Password', form=form)

@users.route("/reset-password<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_password_reset_token(token)
    if not user:
        flash('The password reset link has expired generate new', 'warning')
        return redirect(url_for('users.password_reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pwd
        db.session.commit()
        flash('Your password has been reset', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/new_password.html', title='Set New Password', form=form)

"""_________________________________SETTINGS_______________________________________"""

@users.route('/settings/', methods=['GET'])
@login_required
def settings():
    return redirect(url_for('users.account'))


@users.route('/settings/senders/', methods=['GET', 'POST'])
@login_required
def senders():
    all_senders = Senders.query.filter_by(user=current_user).all()
    return render_template('users/senders.html', active_page='settings', active_settings_page='senders',senders = all_senders)

@users.route('/settings/senders/<sender_id>', methods=['GET', 'POST'])
@login_required
def edit_sender(sender_id):
    sender = Senders.query.get(sender_id)
    form = ConfigurationForm()
    test_response = ""
    if request.method == 'GET':
        form.email.data = sender.email
        form.host.data = sender.host
        form.port.data = sender.port
        form.username.data = sender.username
        form.sender_name.data = sender.sender_name
        form.password.render_kw = {'disabled': False, 'placeholder': '****'}
    if request.method == "POST":
        if form.validate_on_submit():
            result = send_test_email(
                sender_email = form.email.data,
                sender_name = form.sender_name.data,
                host = form.host.data,
                port = int(form.port.data),
                password = form.password.data,
                username = form.username.data,
                receiver_email = form.test_email.data,
                platform = form.platform.data,
            )
            test_response = result
            if test_response[0]:
                sender.email = form.email.data,
                sender.sender_name = form.sender_name.data
                sender.host = form.host.data
                sender.port = form.port.data
                sender.username = form.username.data 
                sender.platform = form.platform.data
                sender.password = form.password.data
                db.session.commit()
                flash('Sender updated', 'success')
                return redirect(url_for('users.senders'))
            
    return render_template('users/edit_sender.html', active_page='settings',
                           test_response=test_response, form=form, active_settings_page='senders', sender=sender)

@users.route('/settings/senders/test-config/<sender_id>', methods=['GET', 'POST'])
@login_required
def test_configuration(sender_id):
    sender = Senders.query.get(sender_id)
    test_response = ""
    if request.method == 'POST':
        receiver_email = request.form.get('receiver_email')
        result = send_test_email(
                sender_email = sender.email,
                sender_name = sender.sender_name,
                host = sender.host,
                port = sender.port,
                password = sender.password,
                username = sender.username,
                receiver_email = receiver_email
            )
        test_response=result
    return render_template('users/test_config.html', sender=sender, test_response=test_response)

@users.route('/settings/senders/configuration/', methods=['GET', 'POST'])
@login_required
def configuration():
    form = ConfigurationForm()
    test_response = ""
    if request.method == "POST":
        if form.validate_on_submit():
            print(form.data)
            result = send_test_email(
                sender_email = form.email.data,
                sender_name = form.sender_name.data,
                host = form.host.data,
                port = int(form.port.data),
                password = form.password.data,
                username = form.username.data,
                receiver_email = form.test_email.data,
                platform = form.platform.data,
            )
            test_response = result
            if test_response[0]:
                sender = Senders(email = form.email.data, sender_name=form.sender_name.data,host=form.host.data,
                                 port = form.port.data, username=form.username.data, platform=form.platform.data,
                                 password=form.password.data, user=current_user)
                db.session.add(sender)
                db.session.commit()
                flash('Sender added', 'success')
                return redirect(url_for('users.senders'))
            else:
                pass
    return render_template('users/configurations.html', active_settings_page='senders', active_page='settings', form=form, test_response=test_response)
 
@users.route('/settings/attributes/', methods=['GET'])
@login_required
def attributes():
    return render_template('users/attributes.html', active_page='settings',)