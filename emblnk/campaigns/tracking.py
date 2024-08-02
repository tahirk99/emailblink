from flask import Blueprint, request, render_template, current_app, redirect, url_for, flash, session, make_response
from emblnk.models import Campaign, CampaignRecipient, CampaignTracking, List, Senders, Contact, Templates
from flask_login import current_user, login_required
from emblnk.campaigns.forms import CampaignInfoForm, MessageForm, TemplateForm
from emblnk import db
from emblnk.campaigns.MailSender import SendCampaign
from emblnk.campaigns.html_email_temp import test_mail_content
from emblnk.models import generate_unique_slug
from datetime import datetime

tracking = Blueprint('tracking', __name__)

@tracking.route("/clicks/<campaign_tracking_id>", methods=['GET'])
def clicks(campaign_tracking_id):
    recipient = CampaignRecipient.query.filter_by(url_slug=campaign_tracking_id).first()
    tracking = CampaignTracking.query.filter_by(recipient_id=recipient.recipient_id).first()
    if tracking:
        tracking.click_count += 1
    else:
        tracking = CampaignTracking(recipient_id=recipient.recipient_id,
                                    click_url=request.args.get('url'), open_count=1, click_count=1, event_name='Clicked', event_time=datetime.utcnow())
        db.session.add(tracking)
    db.session.commit()
    contact = Contact.query.get(recipient.contact_id)
    camp = Campaign.query.get(recipient.campaign_id)
    print(f'{contact} Clicked a link from {camp.campaign_name}')
    return redirect(request.args.get('url', '/'))

@tracking.route("/opens/<campaign_tracking_id>", methods=['GET'])
def opens(campaign_tracking_id):
    recipient = CampaignRecipient.query.filter_by(url_slug=campaign_tracking_id).first()
    tracking = CampaignTracking.query.filter_by(recipient_id=recipient.recipient_id).first()
    if tracking:
        tracking.open_count += 1
    else:
        tracking = CampaignTracking(recipient_id=recipient.recipient_id, open_count=1, click_count=0, event_name='Opened', event_time=datetime.utcnow())
        db.session.add(tracking)
    db.session.commit()
    contact = Contact.query.get(recipient.contact_id)
    camp = Campaign.query.get(recipient.campaign_id)
    print(f'{contact} Opened {camp.campaign_name}')
    return make_response('', 200)
@tracking.route('/unsubscribe/<campaign_tracking_id>')
def unsubscribe(campaign_tracking_id):
    recipient = CampaignRecipient.query.filter_by(url_slug=campaign_tracking_id).first()
    contact = Contact.query.get(recipient.contact_id)
    contact.subscribed = False
    db.session.commit()
    return f'{contact.email} is unsubscribed'

@tracking.route('/tracking/')
def track_test():
    return 'Hello World'