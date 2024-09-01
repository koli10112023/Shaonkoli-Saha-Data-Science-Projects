from flask import Flask, request, render_template as rt , redirect , url_for
from model import * 
import os
from api import *
from sqlalchemy import func

from flask_security import Security, SQLAlchemyUserDatastore, login_required, login_user, logout_user
from flask_security.utils import hash_password, verify_password
#from flask_jwt_extended import JWTManager, create_access_token

from flask_restful import Api


current_dir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(current_dir,"mad-2.sqlite3")
app.config['SECRET_KEY'] = 'superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
#app.config['JWT_SECRET_KEY'] = 'AHUHDDJHUHENOIDJEDJFKJIUIEHJKWN'

db.init_app(app)
#jwt = JWTManager(app)
app.app_context().push()


user_datastore = SQLAlchemyUserDatastore(db, User,Role)
influencer_datastore = SQLAlchemyUserDatastore(db, influencer,Role)

security = Security(app, user_datastore)

api = Api(app)
api.add_resource(sponsor_profile, '/api/sponsor_profile/<username>')
api.add_resource(campaigns, '/api/campaigns/<username>')
api.add_resource(sponsor_campaigns, '/api/sponsor_campaigns/<username>')
api.add_resource(influencer_campaigns, '/api/influencer_campaigns/<username>')
api.add_resource(searchinfluencer, '/api/searchinfluencer/<username>')
api.add_resource(influencer_profile, '/api/influencer_profile/<username>')
api.add_resource(searchcampaign, '/api/searchcampaign/<username>')
api.add_resource(requestinfluencer, '/api/requestinfluencer/<username>')
api.add_resource(sponsoradrequest, '/api/sponsoradrequest/<username>')
api.add_resource(pending_approval, '/api/pending_approval')
api.add_resource(number_of_user,'/api/number_of_user')
api.add_resource(all_user,'/api/all_user')
api.add_resource(popup_campaigns,'/api/popup_campaigns/<username>')


@app.route('/', methods=['GET','POST'])
def home():
    user = User.query.all()
    if not user:
        user_datastore.create_user( 
            username = 'Admin',
            email = 'admin@gmail.com' ,
            password = 'password',
            user_type = 'Admin'
                )
        db.session.commit() 
    return rt('main.html')

@app.route('/submit', methods=['POST'])
def submit():
    submit_button = request.form['submit_button']
    if submit_button == 'Admin Login':
        return redirect(url_for('admin_login'))
    elif submit_button == 'Sponsor Login':
        return redirect(url_for('sponsor_login'))
    elif submit_button == 'Influencer Login':
        return redirect(url_for('influencer_login'))

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email'] 
        password = request.form['password']
        
        admin_data = User.query.filter(User.email == email).filter(func.lower(User.user_type)=='admin').first()
        
        if admin_data:
            if verify_password(password, admin_data.password):
                login_user(admin_data)
                #token = create_access_token(identity=user_data)
                print()
                
                return redirect(url_for('admin_dashboard'))
            return rt('admin_login.html', massage= "Wrong email or password")
        else:
            return rt('admin_login.html', massage= "Wrong email or password")
    return rt('admin_login.html')

@app.route('/sponsor_login', methods=['GET','POST'])
def sponsor_login():
    if request.method == 'POST':
        email = request.form['email'] 
        password = request.form['password']
        
        sponsor_data = User.query.select_from(User).join(sponsor,sponsor.Email==email).filter(User.email == email).filter(func.lower(User.user_type)=='sponsor').filter(sponsor.flagged=='unflag').first()
        if sponsor_data:
            if verify_password(password, sponsor_data.password):
                login_user(sponsor_data)
                #token = create_access_token(identity=user_data)

                return redirect(url_for('sponsor_dashboard',username=sponsor_data.username))
                   
            return rt('sponsor_login.html', massage= "Wrong email or password")
        else:
            return rt('sponsor_login.html', massage= "Wrong email or password")
    return rt('sponsor_login.html')

@app.route('/influencer_login', methods=['GET','POST'])
def influencer_login():
    if request.method == 'POST':
        email = request.form['email'] 
        password = request.form['password']
        
        influencer_data = User.query.select_from(User).join(influencer,influencer.email==email).filter(User.email == email).filter(func.lower(User.user_type)=='influencer').filter(influencer.flagged=='unflag').first()

        
        print()
        if influencer_data:
            if verify_password(password, influencer_data.password):
                login_user(influencer_data)
                #token = create_access_token(identity=user_data)
                
                return redirect(url_for('influencer_dashboard',username=influencer_data.username))
            return rt('influencer_login.html', massage= "Wrong email or password")
        else:
            return rt('influencer_login.html', massage= "Wrong email or password")
    return rt('influencer_login.html')

@app.route('/sponsor_signup', methods=['GET','POST'])
def sponsor_signup():    
    if request.method == 'POST':

        
        if not User.query.filter(User.email == request.form['email']).all():
            username = request.form['username']
            email = request.form['email']  
            password = hash_password(request.form['password'])
            industry = request.form['industry']  
            budget = request.form['budget']  
            bio = request.form['bio']  
            flagged = 'flag'
            user_datastore.create_user( 
            username = username,
            email = email ,
            password = password,
            user_type = 'Sponsor'
                )
            newsponsor = sponsor(Name = username, Email = email, Industry = industry, Budget = budget, Bio = bio, flagged=flagged)
            db.session.add(newsponsor)
            
        
        db.session.commit() 

    return rt('sponsor_signup.html')

@app.route('/influencer_signup', methods=['GET','POST'])
def influencer_signup():    
    if request.method == 'POST':

        
        if not User.query.filter(User.email == request.form['email']).all():
            username = request.form['username']
            email = request.form['email']  
            password = hash_password(request.form['password'])
            category = request.form['category']  
            reach = request.form['reach']  
            bio = request.form['bio']  
            flagged = 'unflag'
            user_datastore.create_user( 
            username = username,
            email = email ,
            password = password,
            user_type = 'Influencer'
                )
            newinfluencer = influencer(name = username, email = email, category = category, reach = reach, bio = bio, flagged = flagged)
            db.session.add(newinfluencer)

        
        db.session.commit() 

    return rt('influencer_signup.html')

@app.route('/forgetpassword', methods=['GET','POST'])
def forgetpassword():    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['conpassword']
        print(password)
        if password == confirm_password:
            user = user_datastore.find_user(email=email)
            print(user)
            if user:
                user.password = hash_password(password)
                print(password)
                db.session.commit()                    
                return rt('main.html')
            else:
                return rt('forgetpassword.html',massage= "Emil ID does not exist")
        else:
            return rt('forgetpassword.html',massage= "Password and confirm password are not same")
    return rt('forgetpassword.html')

@app.route('/admin_dashboard', methods=['GET','POST'])
@login_required
def admin_dashboard():
    return rt('admin.html')

# @app.route('/sponsor_campaign/<username>', methods=['GET'])
#@app.route('/sponsor_profile/<username>', methods=['GET','POST'])
@app.route('/sponsor_dashboard/<username>', methods=['GET','POST'])
@login_required
def sponsor_dashboard(username):
    print(username)
    return rt('sponsor.html',username=username)


@app.route('/update_sponsor/<username>', methods=['GET','POST'])
@login_required
def update_sponsor(username):
    spon = sponsor.query.filter_by(Name=username).first()
    if request.method == 'POST':
        industry = request.form['industry']
        budget = request.form['budget']
        bio = request.form['bio']
        spon.Industry=industry
        spon.Budget=budget
        spon.Bio=bio
        db.session.commit()     
    return rt('sponsor.html',username=username)

@app.route('/create_campaign/<username>', methods = ['GET','POST'])
@login_required
def create_campaign(username):
    sponsor_data = sponsor.query.filter(sponsor.Name==username).first()
    campaign_name = request.form['campaign_name']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    budget = request.form['budget']
    industry = request.form['industry']
    visibility = request.form['visibility']
    
    if request.method == 'POST':
        
            
            if not campaign.query.filter(campaign.name==campaign_name).all():
                newcampaign = campaign(name=campaign_name,description=description,start_date=start_date,end_date=end_date,budget=budget,industry=industry,visibility=visibility)
                
                db.session.add(newcampaign)
                db.session.commit()
                campaign_data = campaign.query.filter(campaign.name==campaign_name).first()
                newlink = spon_influ_camp(spon_id=sponsor_data.ID,camp_id=campaign_data.id)
                db.session.add(newlink)
                print('added')
                db.session.commit()
        
    return rt('sponsor.html',username=username)

@app.route('/update_campaign/<username>',methods=['GET','POST'])
@login_required
def update_campaign(username):
    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        industry = request.form['industry']
        visibility = request.form['visibility']
        campaign_data = campaign.query.select_from(campaign).join(spon_influ_camp, spon_influ_camp.camp_id==campaign.id).join(sponsor,spon_influ_camp.spon_id==sponsor.ID).filter(sponsor.Name==username).filter(campaign.name==campaign_name).first()
        if campaign_data:
            campaign_data.description = description
            campaign_data.start_date = start_date
            campaign_data.end_date = end_date
            campaign_data.budget = budget
            campaign_data.industry = industry
            campaign_data.visibility = visibility
            db.session.commit()
            print('after commit')
    return rt('sponsor.html',username=username)
@app.route('/popup/<username>/<id>',methods=['GET','POST'])
@login_required
def popup(username,id):
    return rt('popup.html',username=username,id=id)

@app.route('/delete_campaign/<username>/<campaign_name>',methods=['GET','POST'])
@login_required
def delete_campaign(username,campaign_name):
    if request.method == 'POST':
        db.session.query(campaign).filter(campaign.name==campaign_name).delete(synchronize_session=False)
        db.session.commit()
    return rt('sponsor.html',username=username,campaign_name=campaign_name)

@app.route('/request_influencer/<username>/<id>',methods=['GET','POST'])
@login_required
def request_influencer(username,id):
    if request.method == 'POST':
        selected_option = request.form.get('option')
        print(selected_option)
        campaign_data = campaign.query.filter(campaign.name==selected_option).first()
        print(campaign_data.id)
        link_data = spon_influ_camp.query.filter(spon_influ_camp.camp_id==campaign_data.id).first()
        print(link_data)
        
        link_data.influ_id = id
        link_data.status = 'pending'
        link_data.request_from = 'sponsor'
        db.session.commit()
    return rt('sponsor.html',username=username,id=id)

@app.route('/request_campaign/<username>/<id>',methods=['GET','POST'])
@login_required
def request_campaign(username,id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(campaign, campaign.id==spon_influ_camp.camp_id).filter(campaign.id==id).first()
        influ_data = influencer.query.filter(influencer.name==username).first()
        message = request.form['message']
        link_data.message = message
        link_data.influ_id = influ_data.id
        link_data.status = 'pending'
        link_data.request_from = 'influencer'
        db.session.commit()
    return rt('influencer.html',username=username,id=id)

@app.route('/status_submit/<username>/<id>',methods=['GET','POST'])
@login_required
def status_submit(username,id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(campaign,campaign.id==spon_influ_camp.camp_id).filter(campaign.id==id).first()
        status = request.form['options']
        print(status)
        link_data.status = status
        db.session.commit()
    return rt('influencer.html',username=username,id=id)

@app.route('/accept_request/<username>/<id>/<camp_id>',methods=['GET','POST'])
@login_required
def accept_request(username,id,camp_id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(sponsor,sponsor.ID==spon_influ_camp.spon_id).filter(sponsor.Name==username).filter(spon_influ_camp.influ_id==id).filter(spon_influ_camp.camp_id==camp_id).first()
        print(link_data)
        link_data.status = 'accepted'
        db.session.commit()
    return rt('sponsor.html',username=username,id=id,camp_id=camp_id)

@app.route('/reject_request/<username>/<id>',methods=['GET','POST'])
@login_required
def reject_request(username,id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(sponsor,sponsor.ID==spon_influ_camp.spon_id).filter(sponsor.Name==username).filter(spon_influ_camp.influ_id==id).first()
        print(link_data)
        link_data.status = 'rejected'
        db.session.commit()
    return rt('sponsor.html',username=username,id=id)

@app.route('/accept_ad_request/<username>/<id>',methods=['GET','POST'])
@login_required
def accept_ad_request(username,id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(influencer,influencer.id==spon_influ_camp.influ_id).filter(influencer.name==username).filter(spon_influ_camp.camp_id==id).first()
        print(link_data)
        link_data.status = 'accepted'
        db.session.commit()
    return rt('influencer.html',username=username,id=id)

@app.route('/reject_ad_request/<username>/<id>',methods=['GET','POST'])
@login_required
def reject_ad_request(username,id):
    if request.method == 'POST':
        link_data = spon_influ_camp.query.select_from(spon_influ_camp).join(influencer,influencer.id==spon_influ_camp.influ_id).filter(influencer.name==username).filter(spon_influ_camp.camp_id==id).first()
        print(link_data)
        link_data.status = 'rejected'
        db.session.commit()
    return rt('influencer.html',username=username,id=id)


@app.route('/accept_sponsor/<id>',methods=['GET','POST'])
@login_required
def accept_sponsor(id):
    if request.method == 'POST':
        sponsor_data = sponsor.query.filter(sponsor.ID==id).filter(sponsor.flagged=='flag').first()
        sponsor_data.flagged = 'unflag'
        db.session.commit()
    
    return rt('admin.html',id=id)

@app.route('/reject_sponsor/<id>',methods=['GET','POST'])
@login_required
def reject_sponsor(id):
    if request.method == 'POST':
        user_data = User.query.select_from(User).join(sponsor, sponsor.Email == User.email).filter(sponsor.ID==id).filter(sponsor.flagged=='flag').first()
        db.session.query(User).filter(User.email==user_data.email).delete(synchronize_session=False)
        db.session.query(sponsor).filter(sponsor.ID==id).delete(synchronize_session=False)
        db.session.commit()
    return rt('admin.html',id=id)

@app.route('/influencer_dashboard/<username>', methods=['GET','POST'])
@login_required
def influencer_dashboard(username):
    print(username)
    return rt('influencer.html',username=username)

@app.route('/update_influencer/<username>',methods=['GET','POST'])
@login_required
def update_influencer(username):
    influ = influencer.query.filter_by(name=username).first()
    if request.method == 'POST':
        category = request.form['category']
        bio = request.form['bio']
        influ.category = category
        influ.bio = bio
        db.session.commit()
    return rt('influencer.html',username=username)

@app.route('/flag_user/<usertype>/<id>/<flagged>',methods=['GET','POST'])
@login_required
def flag_user(usertype,id,flagged):
    if request.method=='POST':
        influencer_data = influencer.query.filter(influencer.id==id).first()
        sponsor_data = sponsor.query.filter(sponsor.ID==id).first()
        if usertype.lower()=='influencer':
            if flagged.lower()=='unflag':
                influencer_data.flagged = 'flag'
            elif flagged.lower() == 'flag':
                influencer_data.flagged = 'unflag'
        if usertype.lower()=='sponsor':
            if flagged.lower()=='unflag':
                sponsor_data.flagged = 'flag'
            elif flagged.lower() == 'flag':
                sponsor_data.flagged = 'unflag'
        db.session.commit()
    return rt('admin.html',usertype=usertype,id=id,flagged=flagged)

@app.route('/delete_user/<usertype>/<id>',methods=['GET','POST'])
@login_required
def delete_user(usertype,id):
    if request.method=='POST':
        if usertype.lower()=='influencer':
            db.session.query(influencer).filter(influencer.id==id).delete(synchronize_session=False)
            db.session.query(spon_influ_camp).filter(spon_influ_camp.influ_id==id).delete(synchronize_session=False)
        if usertype.lower()=='sponsor':
            campaign_data = spon_influ_camp.query.filter(spon_influ_camp.spon_id==id).all()
            db.session.query(sponsor).filter(sponsor.ID==id).delete(synchronize_session=False)
            for item in campaign_data:
                db.session.query(campaign).filter(campaign.id==campaign_data[item].camp_id).delete(synchronize_session=False)
            db.session.query(spon_influ_camp).filter(spon_influ_camp.spon_id==id).delete(synchronize_session=False)
            
        db.session.commit()
    return rt('admin.html',usertype=usertype,id=id)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run(host='0.0.0.0')


