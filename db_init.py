#!/usr/bin/env python

from config import db, engine, db_session
from models import *
from social.apps.flask_app.default import models

def main():
    models.PSABase.metadata.create_all(engine)
    db_session.commit()

    db.create_all()

    fundingCategory = [
        'Summer',
        'Research',
        'Study Abroad',
        'Internship',
        'Travel',
        'Academic Grant',
        'Crowdfunding',
        'Study/Research Grant',
        'Internship/Abroad'
    ]
    for fundingCategory in fundingCategory:
        db.session.add(FundingCategory(name=fundingCategory))

    fundingSchools = [
        ('CFA', 'College of Fine Arts'),
        ('CIT', 'College of Engineering'),
        ('MCS', 'Mellon College of Science'),
        ('TSB', 'Tepper School of Business'),
        ('BXA', 'Interdisciplinary Programs'),
        ('SCS', 'School of Computer Science'),
        ('HSS', 'Dietrich College of Humanities & Social Sciences')
    ]
    for fundingSchool in fundingSchools:
        db.session.add(FundingSchool(*fundingSchool))

    fundingYears = [
        'freshman',
        'sophomore',
        'junior',
        'senior',
        'graduate'
    ]
    for fundingYear in fundingYears:
        db.session.add(FundingYear(name=fundingYear))

    db.session.commit()

if __name__ == '__main__':
    main()
