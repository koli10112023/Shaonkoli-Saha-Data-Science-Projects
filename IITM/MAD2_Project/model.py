from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime


db= SQLAlchemy()

roles_users = db.Table('roles_users',
                       db.Column('user_id',db.Integer,db.ForeignKey('User.id')),
                       db.Column('role_id',db.Integer,db.ForeignKey('Role.id'))
                       )


class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String)
    user_type = db.Column(db.String)
    #role = db.Column(db.String)
    roles = db.relationship('Role',secondary=roles_users, backref=db.backref('users',lazy='dynamic'))
    last_login=db.Column(db.DateTime)
    #API_token = db.Column(db.String, default = None)
    #myPlaylist = db.relationship("playlist",secondary="user_playlist")
    #admin = db.relationship('admin', back_populates='User')
    



    def log_login(self):
        self.last_login=datetime.now()
        db.session.commit()



class Role(db.Model,RoleMixin):
    __tablename__ = 'Role'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    description=db.Column(db.String,nullable=False)


class sponsor(db.Model):
    __tablename__ = 'sponsor'
    ID = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String, unique=True, nullable=False)
    Email = db.Column(db.String, unique=True, nullable=False)
    Industry = db.Column(db.String)
    Budget = db.Column(db.Integer)
    Bio = db.Column(db.String)
    flagged = db.Column(db.String)
    spon_influ_camp = db.relationship('spon_influ_camp', back_populates='sponsor')
    

class influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    category = db.Column(db.String)
    bio = db.Column(db.String)
    reach = db.Column(db.Integer)
    flagged = db.Column(db.String)
    spon_influ_camp = db.relationship('spon_influ_camp', back_populates='influencer')
    

class campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    industry = db.Column(db.String)
    budget = db.Column(db.Integer)
    visibility = db.Column(db.String)
    spon_influ_camp = db.relationship('spon_influ_camp', back_populates='campaign')



class spon_influ_camp(db.Model):
    __tablename__ = 'spon_influ_camp'    
    id = db.Column(db.Integer,primary_key=True)
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsor.ID'))
    influ_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    camp_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    message = db.Column(db.String)
    status = db.Column(db.String)
    request_from = db.Column(db.String)
    campaign = db.relationship('campaign', back_populates='spon_influ_camp')
    sponsor = db.relationship('sponsor', back_populates='spon_influ_camp')
    influencer = db.relationship('influencer', back_populates='spon_influ_camp')
    
