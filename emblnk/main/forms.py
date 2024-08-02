from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, EmailField, SubmitField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileSize
from flask_wtf import FlaskForm
from emblnk.models import Contact
from flask_login import current_user

class UploadContacts(FlaskForm):
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB in bytes
    contacts = FileField('Upload sheet (.csv & .xlsx only) Max = 2 MB', validators=[
        FileAllowed(['csv', 'xlsx'], 'Only CSV and Excel files are allowed.'),
        FileSize(max_size=MAX_FILE_SIZE, message='File size must be less than 2 MB.'),
        DataRequired()
    ])
    submit = SubmitField('Upload')

class AddContact(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    company_name = StringField('Company')
    submit = SubmitField('Add Contact')

    def validate_email(self, email):
        user = Contact.query.filter_by(email=email.data, user=current_user).first()
        print("---------------------------USER Status------------------", user)
        if user:
            raise ValidationError('Email is already registered')

class CreateContactList(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    submit = SubmitField('Create List')

class UpdateContact(FlaskForm):
    pass

class MapContactsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        email_choices = kwargs.pop('email_choices')
        lists = kwargs.pop('lists')
        super(MapContactsForm, self).__init__(*args, **kwargs)
        self.email.choices = email_choices
        self.first_name.choices = choices
        self.last_name.choices = choices
        self.company.choices = choices
        self.lists.choices = lists

    email = SelectField('EMIAIL', validators=[DataRequired()])
    first_name = SelectField('FIRSTNAME', validators=[DataRequired()])
    last_name = SelectField('LASTNAME', validators=[DataRequired()])
    company = SelectField('COMPANY', validators=[DataRequired()])
    lists = SelectField('Choose List')
    submit = SubmitField('Map & Upload')