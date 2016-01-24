#!/usr/bin/env python

from config import db
from flask.ext.login import UserMixin

categories = db.Table('categories',
    db.Column('funding_category_id', db.Integer, db.ForeignKey('funding_category.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id')),
    db.UniqueConstraint('funding_category_id', 'funding_source_id')
)

schools = db.Table('schools',
    db.Column('funding_school_id', db.String(3), db.ForeignKey('funding_school.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id')),
    db.UniqueConstraint('funding_school_id', 'funding_source_id')
)

years = db.Table('years',
    db.Column('funding_year_id', db.Integer, db.ForeignKey('funding_year.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id')),
    db.UniqueConstraint('funding_year_id', 'funding_source_id')
)

sponsors = db.Table('sponsors',
    db.Column('funding_sponsor_id', db.Integer, db.ForeignKey('funding_sponsor.id')),
    db.Column('funding_source_id', db.Integer, db.ForeignKey('funding_source.id')),
    db.UniqueConstraint('funding_sponsor_id', 'funding_source_id')
)

class User(db.Model, UserMixin):
    id = db.Column(db.String(8), primary_key=True) #andrew_id
    additions = db.relationship('FundingSource', backref='added_by')
    admin = db.Column(db.Boolean)
    username = db.Column(db.String(100))
    profile_set = db.Column(db.Boolean, default=False)
    sex = db.Column(db.Integer) # https://en.wikipedia.org/wiki/ISO/IEC_5218
    school = db.ForeignKey('FundingSchool')
    citizen = db.Column(db.Boolean)
    year = db.ForeignKey('FundingYear')

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', kwargs.get('username'))
        self.username = self.id
        self.admin = kwargs.get('admin', False)

    def __repr__(self):
        return 'User <%r>' % self.id

class FundingSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    categories = db.relationship('FundingCategory', secondary=categories, backref=db.backref('sources', lazy='dynamic'), cascade='delete')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('funding_sponsor.id'))
    application = db.Column(db.Text)
    policies = db.Column(db.Text)
    grant_size = db.Column(db.String(250))
    deadline = db.Column(db.DateTime)
    other_info = db.Column(db.Text)
    link = db.Column(db.String(2048))
    independent = db.Column(db.Boolean)

    added_by_id = db.Column(db.String(8), db.ForeignKey('user.id'))

    eligibility = db.Column(db.Text)
    sex = db.Column(db.Integer) # https://en.wikipedia.org/wiki/ISO/IEC_5218
    schools = db.relationship('FundingSchool', secondary=schools, backref=db.backref('sources', lazy='dynamic'), cascade='delete')
    citizen = db.Column(db.Boolean)
    years = db.relationship('FundingYear', secondary=years, backref=db.backref('sources', lazy='dynamic'), cascade='delete')

    def __repr__(self):
        return '<Funding Source %r>' % self.name

class FundingSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    sources = db.relationship('FundingSource', backref='sponsor')

    def __repr__(self):
        return '<Funding Sponsor %r>' % self.name

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
