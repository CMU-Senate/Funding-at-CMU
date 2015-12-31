#!/usr/bin/env python

from config import db
from models import *

def main():
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
        ('HSS', 'H. John Heinz III College'),
        ('TSB', 'Tepper School of Business'),
        ('BXA', 'Interdisciplinary Programs'),
        ('SCS', 'School of Computer Science'),
        ('DET', 'Dietrich College of Humanities & Social Sciences')
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
