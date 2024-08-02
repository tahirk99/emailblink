from wtforms.validators import DataRequired, Email, Optional
from wtforms import StringField, SelectField, RadioField, TextAreaField, DateTimeField, SubmitField
from flask_wtf import FlaskForm
from emblnk.models import List
from flask_login import current_user

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

"""class ListForm(FlaskForm):
    to_lists = QuerySelectMultipleField('Select a contact lists', query_factory=lambda: List.query.filter_by(user=current_user).order_by(List.list_name).all(), get_label='list_name')


class ListForm(FlaskForm):
    to_lists = QuerySelectMultipleField('Select contact lists', query_factory=lambda: List.query.filter_by(user=current_user).order_by(List.list_name).all())

    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)

class ListsAndSchedule(FlaskForm):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(ListsAndSchedule, self).__init__(*args, **kwargs)
        self.to_lists.choices = choices

    to_lists = SelectMultipleField('Select contact lists')
    #submit = SubmitField('Create Campaign')"""

class CampaignInfoForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(CampaignInfoForm, self).__init__(*args, **kwargs)
        self.sender.choices = choices

    sender = SelectField('Select a Sender', validators=[DataRequired()])
    sender_name = StringField('Define Sender Name (Optional)')
    campaign_name = StringField('Campaign Name', validators=[DataRequired()])
    reply_to = StringField('Reply-to address (Optional)', validators=[Optional(), Email()])
    subject_line = StringField('Subject', validators=[DataRequired()])
    pre_text_loader = StringField('Pre-text Loader (Optional)',)
    #submit = SubmitField('Save & Next')

class CampaignTemplateForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(CampaignTemplateForm, self).__init__(*args, **kwargs)
        self.template.choices = choices
    template = SelectField('Choose a Template', validators=[DataRequired()])

class MessageForm(FlaskForm):
    message = TextAreaField('Create a Message', validators=[DataRequired()])
    #submit = SubmitField('Create Message & Next')

class TemplateForm(FlaskForm):
    template_name = StringField('Template Name', validators=[DataRequired()])
    message = TextAreaField('Message (Email HTML)', validators=[DataRequired()])
    submit = SubmitField('Save & Exit')