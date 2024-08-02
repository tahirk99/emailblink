from emblnk import db, login_manager
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import secrets

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

def generate_unique_slug(user_id, length=8, int_only=True):
    characters = "0123456789" if int_only else "0123456789dadabcdeaugafghijklmnfopqrstuvwxyzcymja8abqoayadpqhqondkuamslmnhtheuqzvcajsgwtwgyiip"
    unique_string = str(user_id)
    
    while len(unique_string) <= length:
        unique_string += secrets.choice(characters)
    
    if len(unique_string) > length:
        unique_string = unique_string[:length]

    return unique_string

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    upload_file = db.Column(db.String(20))
    password = db.Column(db.String(60), nullable=False)
    company = db.Column(db.String(120))
    contacts = db.relationship('Contact', backref='user', lazy=True)
    contact_lists = db.relationship('List', backref='user', lazy=True)
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    #messages = db.relationship('Message', backref='user', lazy=True)
    templates = db.relationship('Templates', backref='user', lazy=True)
    senders = db.relationship('Senders', backref='user', lazy=True)
    def get_password_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps({'user_id':self.id}, salt='token')
        return token

    @staticmethod
    def verify_password_reset_token(token):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, salt='token', max_age=1800)['user_id']
        except Exception as e:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User({self.id}: '{self.username}', '{self.email}', '{self.image_file}', '{self.upload_file}')"

contact_and_lists = db.Table('contact_and_lists', 
                             db.Column('contact_id', db.Integer, db.ForeignKey('contact.contact_id')),
                             db.Column('list_id', db.Integer, db.ForeignKey('list.list_id')))


class Senders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255), default=email)
    username = db.Column(db.String(255), default=email)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_primary = db.Column(db.Boolean)
    campaigns = db.relationship('Campaign', backref='sender', lazy=True)

class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), nullable=False, unique=False)
    company = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.now)
    contact_lists = db.relationship('List', secondary=contact_and_lists, backref='contacts')
    slug = db.Column(db.String(8), unique=True, default=generate_unique_slug(2), nullable=False)
    subscribed = db.Column(db.Boolean, default=True)

class List(db.Model):
    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(120), default='Default List')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    slug = db.Column(db.String(5), default=generate_unique_slug(2, length=5), unique=True, nullable=False)

    def __repr__(self):
        return (self.list_id, self.list_name, False, {})

campaign_to_list = db.Table('campaign_to_list',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.campaign_id')),
    db.Column('list_id', db.Integer, db.ForeignKey('list.list_id')))

campaign_to_contacts = db.Table('campaign_to_contacts',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.campaign_id')),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.contact_id')))

class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('senders.id'), nullable=False)
    campaign_name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    pre_loader = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    recipients = db.relationship('CampaignRecipient', backref='campaign', lazy=True)
    message = db.Column(db.String(1000000))
    to_lists = db.relationship('List', secondary='campaign_to_list', backref='campaigns')
    to_contacts = db.relationship('Contact', secondary='campaign_to_contacts', backref='campaigns')
    campaign_status = db.Column(db.String(20), default='Draft')
    total_clicks = db.Column(db.Integer)
    unique_clicks = db.Column(db.Integer)
    total_opens = db.Column(db.Integer)
    unique_opens = db.Column(db.Integer)
    total_contacts = db.Column(db.Integer)
    #total_sent = db.Column(db.Integer)
    total_ubsubscribes = db.Column(db.Integer)
    slug = db.Column(db.String(32), default=generate_unique_slug(2, length=32, int_only=False), nullable=False, unique=True)

class Templates(db.Model):
    template_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    message = db.Column(db.String(1000000))
    #is_template_message = db.Column(db.Boolean, default=True)
    slug = db.Column(db.String(64), unique=True, default=generate_unique_slug(2, length=64, int_only=False), nullable=False)

#--------Tracking Tables-----------
class CampaignRecipient(db.Model):
    recipient_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.contact_id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)
    url_slug = db.Column(db.String(64), nullable=False)
    tracking = db.relationship('CampaignTracking', back_populates='recipient')
    event_tracking = db.relationship('EventTracking', back_populates='recipient')
    delivered_at = db.Column(db.DateTime)

class CampaignTracking(db.Model):
    tracking_id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('campaign_recipient.recipient_id'), nullable=False)
    click_count = db.Column(db.Integer)
    open_count = db.Column(db.Integer)
    event_name = db.Column(db.String(120))
    click_url = db.Column(db.String(300))
    event_time = db.Column(db.DateTime, default=datetime.now)
    recipient = db.relationship('CampaignRecipient', back_populates='tracking')

class EventTracking(db.Model):
    tracking_id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('campaign_recipient.recipient_id'), nullable=False)
    event_name = db.Column(db.String(120))
    click_url = db.Column(db.String(1200))
    event_time = db.Column(db.DateTime, default=datetime.now)
    recipient = db.relationship('CampaignRecipient', back_populates='event_tracking')