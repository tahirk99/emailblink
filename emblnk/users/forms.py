from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wtforms import StringField, IntegerField ,PasswordField, EmailField, BooleanField, SubmitField, TextAreaField, SelectField
from emblnk.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from flask_login import current_user


class RegisterationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, uname):
        user = User.query.filter_by(username=uname.data).first()
        if user:
            raise ValidationError('Username is already taken')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=2, max=20)])
    email = EmailField('Email', validators=[Optional(), Email()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(min=10, max=120)])
    picture = FileField('Update Profile Pic', validators=[FileAllowed(['jpeg', 'png', 'jpg']), Optional()])
    submit = SubmitField('Update Profile')
    show_email = BooleanField('Hide Email')
    def validate_username(self, uname):
        if uname.data != current_user.username:
            user = User.query.filter_by(username=uname.data).first()
            if user:
                raise ValidationError('Username is already taken')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = EmailField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Reset Password')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email does not exist please create an account')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class ConfigurationForm(FlaskForm):
    platform = SelectField('Select Platform', validators=[DataRequired()], choices=['AWS (SeS)', 'Azure', 'GCP', 'Gmail(500 Maxy/day)', 'Other'])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    host = StringField('Host', validators=[DataRequired()])
    sender_name = StringField('Sender name')
    port = StringField('Port', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    test_email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Test & Add')

    def validate_port(self, port):
        try:
            int(port.data)
        except Exception:
            raise ValidationError('Please enter accurate port (number)')

class ConfigurationTestForm(FlaskForm):
    email = EmailField('Enter email to send test mail', validators=[DataRequired(), Email()])
    test_btn = SubmitField('Submit')

class AttributesForm(FlaskForm):
    pass