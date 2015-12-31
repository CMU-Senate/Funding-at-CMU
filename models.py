#!/usr/bin/env python

from config import db

categories = db.Table('categories',
    db.Column('funding_category_id', db.Integer, db.ForeignKey('funding_category.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id'))
)

schools = db.Table('schools',
    db.Column('funding_school_id', db.String(3), db.ForeignKey('funding_school.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id'))
)

years = db.Table('years', 
    db.Column('funding_year_id', db.Integer, db.ForeignKey('funding_year.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id'))
)

class User(db.Model):
    id = db.Column(db.String(8), primary_key=True) #andrew_id
    additions = db.relationship('FundingSource', backref='added_by')

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'User <%r>' % self.id

class FundingSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    categories = db.relationship('FundingCategory', secondary=categories, backref=db.backref('sources', lazy='dynamic'))
    sponsor = db.Column(db.String(250))
    application = db.Column(db.Text)
    policies = db.Column(db.Text)
    grant_size = db.Column(db.String(250))
    deadline = db.Column(db.DateTime)
    other_info = db.Column(db.Text)
    link = db.Column(db.String(2048))

    added_by_id = db.Column(db.String(8), db.ForeignKey('user.id'))

    eligibility = db.Column(db.Text)
    sex = db.Column(db.Integer) # https://en.wikipedia.org/wiki/ISO/IEC_5218
    schools = db.relationship('FundingSchool', secondary=schools, backref=db.backref('sources', lazy='dynamic'))
    citizen = db.Column(db.Boolean)
    years = db.relationship('FundingYear', secondary=years, backref=db.backref('sources', lazy='dynamic'))

class FundingCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<Funding Category %r>' % self.name

class FundingSchool(db.Model):
    id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Funding School %r>' % self.name

class FundingYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)

    def __repr__(self):
        return '<Funding Year %r>' % self.name.title()
