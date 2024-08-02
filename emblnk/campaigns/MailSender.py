import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from emblnk.models import Senders, List, CampaignRecipient, generate_unique_slug
from emblnk import db
from flask import session
import re
from flask import url_for
from bs4 import BeautifulSoup
from flask_login import current_user
from datetime import datetime


def test_mail(sender, receiver_email, subject, message, is_campaign_test_mail=True):
    """This function will be called when user wants to send a test mail"""
    sender_name = sender.sender_name
    sender_email = sender.email
    username = sender.username
    host = sender.host
    port = sender.port
    password =  sender.password
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.add_header("reply-to", sender_email)
    message_html = message
    msg.attach(MIMEText(message_html, "html"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            return True, "<span>✅ Sent Successfully (Check junk, if still haven't recieved <a style='text-decoration:underline;' href='/settings/senders/' target='_blank'>Test sender configuration</a>)</span>"
    except Exception as e:
        if is_campaign_test_mail:
            return False, f"❌ Oops, Failed to send test mail from {sender_email}. Please <a style='text-decoration:underline;' href='/settings/senders/' target='_blank'>Test sender configurations</a>"
        return False, "❌ Oops, there is some issue with your credentials. Refer below for more info.", e
    

def send_test_email(sender_name, receiver_email, sender_email, host, port, username, password):
    """This function will be called when a new sender is being added to test the configuration before creating a sender"""
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = 'Test Email From Emailblink'
    msg.add_header("reply-to", sender_email)

    message_html = f"<p>Hi,</p><p>This is a test email from Emailblink sent via {sender_email}.</p>"

    msg.attach(MIMEText(message_html, "html"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return True, "✅ Sent Successfully (Ignore below message if you have recieved test mail)", """Check junk, if you haven't recieved yet. 
        you might need to check your ESP(Email service provider) if you have ran out of credit limit or your supscription might have been expired. 
        When a test mail is sent successfully it indicates there's no issue with the configuration(credentials)"""
    except Exception as e:
        return False, '❌ Oops, there is some issue with your credentials. Refer below for more info.', e

def send_error_mail(reciever, campaign, contact, message):
    sender = Senders.query.filter_by(user=current_user).first()
    msg = MIMEMultipart()
    msg["From"] = f"{sender.sender_name} <{sender.email}>"
    msg["To"] = reciever
    msg["Subject"] = 'Error occured while sending campaign'

    message_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <p>Hi {current_user.name},</p>

            <p>while sending campaign ({campaign.name}) to {contact.email} an error occured below is the error information.</p>

            <p><strong>Error:&nbsp;</strong><br>{message}</p>

            <p>Regards,</p>

            <p>Emailblink.</p>
        </body>
        </html>"""

    msg.attach(MIMEText(message_html, "html"))

    try:
        with smtplib.SMTP(sender.host, sender.port) as server:
            server.starttls()
            server.login(sender.username, sender.password)
            server.send_message(msg)
        return True, "✅ Sent Successfully"
    except Exception as e:
        return False, '❌ Oops, there is some problem with your credentials. Refer below for more info.', e


class SendCampaign:
    
    def __init__(self, lists, sender_id, subject, message, campaign):
        self.lists = lists
        self.subject = subject
        self.sender = Senders.query.get(sender_id)
        self.message = message
        self.campaign = campaign

    def send_mail(self):
        sent_list = []
        with smtplib.SMTP(self.sender.host, self.sender.port) as server:
            server.starttls()
            server.login(self.sender.username, self.sender.password)
            self.campaign.campaign_status = 'Sending'
            db.session.commit()
            for id in self.lists:
                contact_list = List.query.get(int(id))
                for contact in contact_list.contacts:
                    if not contact.email in sent_list and contact.subscribed:
                        recipient = CampaignRecipient(campaign=self.campaign, contact_id=contact.contact_id, sent_at=datetime.utcnow(),
                                                    url_slug=generate_unique_slug(1, int_only=False, length=64))
                        db.session.add(recipient)
                        msg = MIMEMultipart()
                        msg["From"] = f"{self.sender.sender_name} <{self.sender.email}>"
                        msg["To"] = contact.email
                        msg["Subject"] = self.subject
                        msg.add_header("reply-to", self.sender.email)
                        message_html = self.personalize_message(self.message,contact=contact, campaign_tracking_id=recipient.url_slug)
                        msg.attach(MIMEText(message_html, "html"))
                        server.send_message(msg)
                        sent_list.append(contact.email)
                        #self.campaign.total_sent = len(sent_list)
                        db.session.commit()
                        print(f'{self.campaign} sent to {contact.email}')

        sent_list.clear()
        self.campaign.campaign_status = 'Sent'
        db.session.commit()
        return True, "✅ Sent Successfully"
    
    def personalize_message(self, message, contact, campaign_tracking_id):
        unsubscribe_url = url_for('tracking.unsubscribe', campaign_tracking_id=campaign_tracking_id, _external=True)# slug=contact.slug, campaign_id=campaign.campaign_id)
        message = message.replace('%UNSUBSCRIBE%', unsubscribe_url)

        placeholders = re.findall(r'%([^%]+)%', message)
        for placeholder in placeholders:
            value = getattr(contact, placeholder, '')
            message = message.replace(f'%{placeholder}%', str(value))
        
        open_tracking_url = url_for('tracking.opens', campaign_tracking_id=campaign_tracking_id, _external=True)
        open_tracking_pixel = f'<img src="{open_tracking_url}" width="1" height="1" style="display:none;">'
        if '</body>' in message:
            message = message.replace('</body>', f'{open_tracking_pixel}</body>')
        else:
            message = str(message)+open_tracking_pixel
    
        # Replace hrefs for click tracking
        soup = BeautifulSoup(message, 'html.parser')
        for link in soup.find_all('a', href=True):
            if 'unsubscribe' not in link['href']:
                click_tracking_url = url_for('tracking.clicks', url=link['href'], campaign_tracking_id=campaign_tracking_id, _external=True)
                link['href'] = click_tracking_url
            """elif 'unsubscribe' in link['href']:
                link['href'] = str(link['href']).replace('https', '').replace('http', '').replace('/', '').replace(':', '')"""
                
        return str(soup)