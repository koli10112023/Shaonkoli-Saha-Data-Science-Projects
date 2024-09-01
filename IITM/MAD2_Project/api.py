from flask_restful import Resource,reqparse
from model import *
import json
#from flask_jwt_extended import jwt_required
from flask import Flask, jsonify

class sponsor_profile(Resource):
    def get(self,username):
        print(username)
        sponsor_data = sponsor.query.filter(sponsor.Name==username).all()
        print(sponsor_data)
        data = {}
        
        for item in sponsor_data:
            data['Name'] = [item.Name]
            data['Email'] = [item.Email]
            data['Industry'] = [item.Industry]
            data['Budget'] = [item.Budget]
            data['Bio'] = [item.Bio]
        
        json_data = json.dumps(data)
        return  json_data
    
class influencer_profile(Resource):
    def get(self,username):
        print(username)
        influencer_data = influencer.query.filter(influencer.name==username).all()
        print(influencer_data)
        data = {}
        for item in influencer_data:
            data['name'] = [item.name]
            data['email'] = [item.email]
            data['category'] = [item.category]
            data['bio'] = [item.bio]
            data['reach'] = [item.reach]
        json_data = json.dumps(data)
        return json_data

class campaigns(Resource):
    def get(self,username):
        campaign_data = campaign.query.all()
        print(campaign_data)
        data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'start_date': item.start_date,
                    'end_date': item.end_date,
                    'industry': item.industry,
                    'budget' :item.budget,
                    'visibility' :item.visibility
                }
                    for item in campaign_data
                ]
    
    # Return data as JSON
        return jsonify(data)

class sponsor_campaigns(Resource):
    def get(self,username):
        campaign_data = campaign.query.select_from(campaign).join(spon_influ_camp,spon_influ_camp.camp_id==campaign.id).join(sponsor,sponsor.ID==spon_influ_camp.spon_id).filter(sponsor.Name==username).all()       
        print(campaign_data)
        data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'start_date': item.start_date,
                    'end_date': item.end_date,
                    'industry': item.industry,
                    'budget' :item.budget,
                    'visibility' :item.visibility
                }
                    for item in campaign_data
                ]
    
    # Return data as JSON
        return jsonify(data)
    
class influencer_campaigns(Resource):
    def get(self,username):
        campaign_data = campaign.query.select_from(campaign).join(spon_influ_camp,spon_influ_camp.camp_id==campaign.id).join(influencer,influencer.id==spon_influ_camp.influ_id).filter(influencer.name==username).filter(spon_influ_camp.status!='rejected').filter(spon_influ_camp.status!='pending').all()       
        data = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'start_date': item.start_date,
                'end_date': item.end_date,
                'industry': item.industry,
                'budget' :item.budget,
                'visibility' :item.visibility
            }
                for item in campaign_data
        ]      
        return jsonify(data)

class campaigns(Resource):
    def get(self,username):
        campaign_data = campaign.query.all()
        print(campaign_data)
        data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'start_date': item.start_date,
                    'end_date': item.end_date,
                    'industry': item.industry,
                    'budget' :item.budget,
                    'visibility' :item.visibility
                }
                    for item in campaign_data
                ]
    
    # Return data as JSON
        return jsonify(data)    
    
class popup_campaigns(Resource):
    def get(self,username):
        campaign_data = campaign.query.select_from(campaign).join(spon_influ_camp,spon_influ_camp.camp_id==campaign.id).join(sponsor,sponsor.ID==spon_influ_camp.spon_id).filter(sponsor.Name==username).all()
        print(campaign_data)
        data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'start_date': item.start_date,
                    'end_date': item.end_date,
                    'industry': item.industry,
                    'budget' :item.budget,
                    'visibility' :item.visibility
                }
                    for item in campaign_data
                ]
    
    # Return data as JSON
        return jsonify(data)    
    
class searchinfluencer(Resource):
    def get(self,username):
        influencer_data = influencer.query.all()
        data = [
                {
                    'id' : item.id,
                    'name': item.name,
                    'email': item.email,
                    'category': item.category,
                    'bio': item.bio,
                    'reach': item.reach
                }
                    for item in influencer_data
                ]
    
    # Return data as JSON
        return jsonify(data)
class searchcampaign(Resource):
    def get(self,username):
        campaign_data = campaign.query.all()
        data = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'start_date': item.start_date,
                'end_date': item.end_date,
                'industry': item.industry
            }
                for item in campaign_data
        ]
        return jsonify(data)

class requestinfluencer(Resource):
    def get(self,username):
        all_data = spon_influ_camp.query.select_from(spon_influ_camp).join(influencer, influencer.id==spon_influ_camp.influ_id).join(campaign, campaign.id==spon_influ_camp.camp_id).join(sponsor, sponsor.ID==spon_influ_camp.spon_id).filter(sponsor.Name==username).filter(spon_influ_camp.request_from=='influencer').filter(spon_influ_camp.status=='pending').all()
        data = []
        for item in all_data:
            influencer_data = influencer.query.filter(influencer.id==item.influ_id).first()
            campaign_data = campaign.query.filter(campaign.id==item.camp_id).first()
            data.append({
                'id': influencer_data.id,
                'camp_id': campaign_data.id,
                'influencer_name': influencer_data.name,
                'campaign_name': campaign_data.name,
                'message': item.message,
                'status': item.status,
            })
        return jsonify(data)

class sponsoradrequest(Resource):
    def get(self,username):
        campaign_data = campaign.query.select_from(campaign).join(spon_influ_camp, spon_influ_camp.camp_id==campaign.id).join(influencer, spon_influ_camp.influ_id==influencer.id).join(sponsor, sponsor.ID==spon_influ_camp.spon_id).filter(influencer.name==username).filter(spon_influ_camp.status=='pending').filter(spon_influ_camp.request_from=='sponsor').all()
        data = []
        for item in campaign_data:
            data.append({
                'id' : item.id,
                'campaign':item.name,
                'requirement':item.description,
                'payment':item.budget
            })
        return jsonify(data)
    
class pending_approval(Resource):
    def get(self):
        sponsor_data = sponsor.query.filter(sponsor.flagged == 'flag').all()
        data = []
        for item in sponsor_data:
            data.append({
                'id' : item.ID,
                'name' : item.Name,
                'industry' : item.Industry,
                'budget' : item.Budget,
                'bio' : item.Bio

            })    
        return jsonify(data)
    
class number_of_user(Resource):
    def get(self):
        influencer_count = influencer.query.count()
        sponsor_count = sponsor.query.count()
        campaign_count = campaign.query.count()
        data = {
            'influencer' : influencer_count,
            'sponsor' : sponsor_count,
            'campaign' : campaign_count
        }
        json_data = json.dumps(data)
        return  json_data
    
class all_user(Resource):
    def get(self):
        influencer_data = influencer.query.all()
        sponsor_data = sponsor.query.all()
        data = []
        for item in influencer_data:
            completed_campaigns = spon_influ_camp.query.filter(spon_influ_camp.influ_id==item.id).filter(spon_influ_camp.status=='Completed').count()
            data.append(
                {
                    'id':item.id,
                    'name' : item.name,
                    'email' : item.email,
                    'bio' : item.bio,
                    'category' : item.category,
                    'user_type' : 'Influencer',
                    'flagged':item.flagged,
                    'number_of_camp': completed_campaigns
                }
            )
            
            
        
        for item in sponsor_data:
            completed_campaigns = spon_influ_camp.query.filter(spon_influ_camp.spon_id==item.ID).filter(spon_influ_camp.status=='Completed').count()
            data.append(
                {
                    'id':item.ID,
                    'name' : item.Name,
                    'email' : item.Email,
                    'bio' : item.Bio,
                    'category' : item.Industry,
                    'user_type' : 'Sponsor',
                    'flagged':item.flagged,
                    'number_of_camp': completed_campaigns
                }
            )
        
        return jsonify(data)