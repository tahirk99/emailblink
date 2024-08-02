from flask import Blueprint, request, render_template, current_app, redirect, url_for, flash, session, make_response, jsonify
from emblnk.models import Campaign, List, Senders, Templates
from flask_login import current_user, login_required
from emblnk.campaigns.forms import CampaignInfoForm, MessageForm, CampaignTemplateForm
from emblnk import db, scheduler
from emblnk.campaigns.MailSender import SendCampaign, test_mail
from emblnk.models import generate_unique_slug
from datetime import datetime

campaign = Blueprint('campaigns', __name__)

def clear_campaign_session_data():
    campaign_sessions = ['campaign_name', 'subject', 'pre_text_loader', 'session', 'sender', 'step',
                        'message', 'sender_name', 'template', 'to_lists',]
    for key in list(session.keys()):
        if key in campaign_sessions:
            session.pop(key, None)

def add_lists_and_contacts_in_campaign(lists, campaign):
    for i in lists:
        list_ = List.query.get(i)
        if list_:
            campaign.to_lists.append(list_)
            for contact in list_.contacts:
                campaign.to_contacts.append(contact)
            db.session.commit()
    return True


def check_unsubscribe_link(message):
    return True if "%UNSUBSCRIBE%" in message else False

@campaign.route('/campaigns')
@login_required
def campaigns():
    is_campaign = Campaign.query.filter_by(user=current_user).first()
    is_campaign = True if is_campaign else False
    page = request.args.get('page', type=int, default=1)
    show_camps = request.args.get('show', 'All')
    search_camps = request.args.get('query', '')
    page = request.args.get('page', type=int, default=1)
    filter_parameter = None
    if show_camps == 'All':
        campaigns = Campaign.query.filter_by(user=current_user).order_by(Campaign.created_at.desc()).paginate(page=page, per_page=10)
    else:
        filter_parameter = f'show={show_camps}'
        campaigns = Campaign.query.filter_by(user=current_user, campaign_status=show_camps).order_by(Campaign.created_at.desc()).paginate(page=page, per_page=10)
    if search_camps:
        filter_parameter = f'query={search_camps}'
        campaigns = Campaign.query.filter_by(user=current_user).filter(
            Campaign.campaign_name.ilike(f"%{search_camps}%")
        ).order_by(Campaign.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('campaigns/campaigns.html', title='Campaigns', is_campaign=is_campaign,
                           filter_parameter=filter_parameter, campaigns=campaigns, active_page='campaigns')

@campaign.route('/campaigns/<camp_id>')
@login_required
def view_campaign_details(camp_id):
    campaign = Campaign.query.get(camp_id)
    to_lists = campaign.to_lists
    return render_template('/campaigns/campaign_details.html',active_page='campaigns', campaign=campaign, lists=to_lists)

@campaign.route("/templates")
@login_required
def templates():
    page = request.args.get('page', type=int, default=1)
    templates = Templates.query.filter_by(user=current_user).order_by(Templates.created_at.desc()).paginate(page=page, per_page=10)
    total_templates = templates.total
    return render_template('campaigns/templates.html', title='Templates',total_templates=total_templates, templates=templates, active_page='templates',)

@campaign.route('/templates/delete_template', methods=['GET', 'POST'])
@login_required
def delete_template():
    temp_id = request.args.get('temp_id')
    temp = Templates.query.get(temp_id)
    db.session.delete(temp)
    db.session.commit()
    flash("Template deleted successfully", "success")
    return redirect(url_for('campaigns.templates'))   

@campaign.route("/templates/<slug>")
@login_required
def template_view(slug):
    temp = Templates.query.filter_by(slug=slug).first()
    message = temp.message
    temp_name = temp.template_name
    return render_template('campaigns/template_view.html', message=message, temp_name=temp_name)

@campaign.route('/templates/new', methods=['GET', 'POST'])
@login_required
def create_template():
    if request.method == "POST":
        temp_name = request.form['template_name']
        edioter_data = request.form['edioterdata']
        if edioter_data != "" and temp_name !="":
            template = Templates(user=current_user, user_id=current_user.id, template_name=temp_name,
                                message=edioter_data, slug=generate_unique_slug(2, length=64, int_only=False))
            db.session.add(template)
            db.session.commit()
            flash('Template Created', 'success')
            return redirect(url_for('campaigns.templates'))
        else:
            flash('Oops! please fill both the fields', 'danger')
    return render_template('campaigns/create_template.html',active_page='templates')

@campaign.route('/new-campaign/', methods=['GET', 'POST'])
@login_required
def new_campaign():
    #clear_campaign_session_data()
    print(session)
    senders = Senders.query.filter_by(user=current_user).all()
    if senders == []:
        flash("Create a sender before creating campaign", "info")
        return redirect(url_for('users.senders'))
    if not 'step' in session:
        session['step'] = 1
    if not session['step'] == 4:
        session['campaign_preview_data'] = {}
    sender_list = [(i.id, i.email) for i in senders]
    campaign_info_form = CampaignInfoForm(choices=sender_list)
    templates = Templates.query.filter_by(user=current_user).order_by(Templates.created_at).all()
    temp_list = [(i.template_id, i.template_name) for i in templates]
    template_form = CampaignTemplateForm(choices=temp_list)
    message_form = MessageForm()
    lists = List.query.filter_by(user=current_user).order_by(List.list_name).all()
    all_lists = [(i.list_id, i.list_name) for i in lists]
    unsubscribe_warning = False
    sender = Senders.query.get(int(session['sender'])) if 'sender' in session else None
    message = Templates.query.get(int(session['template'])).message if 'template' in session else ''
    if request.method == 'POST':
        is_btn_click = request.form.get('is_btn_click')
        list_form = request.form.getlist('lists')
        send_option = request.form.get('send_options')
        send_test_mail_form = request.form.get('test-mail')
        create_msg = request.form.get('edioterdata')
        unsubscribe_ignore = request.form.get('unsubscribe_ignore')
        if unsubscribe_ignore:
            session['step'] = 3
        if is_btn_click:
            session['step'] = 1
        elif campaign_info_form.validate_on_submit():
            session['campaign_name'] = campaign_info_form.campaign_name.data
            session['subject'] = campaign_info_form.subject_line.data
            session['pre_text_loader'] = campaign_info_form.pre_text_loader.data
            session['sender'] = campaign_info_form.sender.data
            sender = Senders.query.get(int(session['sender']))
            session['sender_name'] = sender.sender_name
            session['step'] = 2
        elif template_form.validate_on_submit():
            temp = Templates.query.get(int(template_form.template.data))
            message = temp.message
            session['template'] = template_form.template.data
            if not check_unsubscribe_link(message):
                unsubscribe_warning = True
                session['step'] = 2
            else:
                session['step'] = 3
        elif create_msg:
            print("CREATE MESSAGE ------------------")
            template = Templates(user=current_user, user_id=current_user.id, template_name=session['campaign_name'],
                                message=create_msg, slug=generate_unique_slug(current_user.id, length=64, int_only=False))
            db.session.add(template)
            db.session.commit()
            session['template'] = template.template_id            
            if not check_unsubscribe_link(template.message):
                session['step'] = 2
                unsubscribe_warning = True
            else:
                session['step'] = 3
        elif list_form:
            session['to_lists'] = list_form
            session['step'] = 4
            campaign_preview_data = {}
            campaign_preview_data['to_lists'] = []
            campaign_preview_data['total_contacts'] = 0
            for i in session['to_lists']:
                li_ = List.query.get(i)
                campaign_preview_data['to_lists'].append(li_.list_name)
                campaign_preview_data['total_contacts'] += len(li_.contacts)
            campaign_preview_data['sender'] = sender.email, sender.sender_name
            session['campaign_preview_data'] = campaign_preview_data
            #add_lists_and_contacts_in_campaign(list_form, campaign=camp)
        elif send_test_mail_form:
            receiver_email = request.form.get('test-mail')
            send_test_mail = test_mail(sender, receiver_email, subject=f"TEST - {session['subject']}", message=message, is_campaign_test_mail=True)
            flash(send_test_mail[1], "success" if send_test_mail else "danger")

        elif send_option:
            #from apscheduler.schedulers.background import BackgroundScheduler
            from datetime import datetime
            sender = Senders.query.get(session['sender'])
            if send_option == 'now':
                NewCampaign = Campaign(
                    user = current_user,
                    campaign_name = session['campaign_name'],
                    subject = session['subject'],
                    pre_loader = session['pre_text_loader'],
                    message = message,
                    sender = sender,
                    campaign_status = "Sending",
                    slug = generate_unique_slug(current_user.id,
                                                length=32, int_only=False))
                db.session.add(NewCampaign)
                add_lists_and_contacts_in_campaign(session['to_lists'], campaign=NewCampaign)
                db.session.commit()
                lists_ = session['to_lists']
                sender_id = int(session['sender'])
                sub = session['subject']
                
                #Send campaign in the background
                @scheduler.task('date', run_date=datetime.now())
                def send_campaign_in_background():
                    with scheduler.app.app_context():
                        send_campaign = SendCampaign(
                            lists= lists_,
                            sender_id= sender_id,
                            subject= sub,
                            message=str(message),
                            campaign=NewCampaign)
                        send_campaign.send_mail()
            
            clear_campaign_session_data()
            #flash('Campaign created successfully', 'success')
            return redirect(url_for('campaigns.campaigns'))
    return render_template('campaigns/new1.html', step=session["step"], active_page='campaigns', message = message,
                            campaign_info_form=campaign_info_form, message_form=message_form, template_form = template_form,
                            lists=all_lists, unsubscribe_warning=unsubscribe_warning)

@campaign.route('/campaigns/<campaign_id>')
@login_required
def campaign_details(campaign_id):
    campaigns = Campaign.query.filter_by(campaign_id=campaign_id).first()
    return render_template('campaigns/campaign_details.html', title='Contacts',active_page='campaigns', campaigns=campaigns)