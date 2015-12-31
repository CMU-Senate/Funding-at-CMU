import csv
import requests
import datetime
import logging
from models import *
from config import db

andrewIDs = {
	'Michael': 'mcgormle',
	'Aashir': 'amaster',
	'Jeannie': 'jemichae',
	'Nadia': 'nrazek',
	'Shelly': 'sbalassy',
	'Stephanie': 'semore'
}

fundingSchools = {
	'3': 'CFA',
	'4': 'CIT',
	'5': 'MCS',
	'6': 'HSS',
	'7': 'TSB',
	'8': 'BXA',
	'11': 'SCS'
}

fundingYears = {
	'9': 'freshman',
    'A': 'sophomore',
    'B': 'junior',
    'C': 'senior',
    'D': 'graduate'
}

def process_source(i, source):
	name = source['Name']
	application = source['How to apply']
	policies = source['Policies/Rules']
	grant_size = source['Size of grant/max possible']
	deadline = datetime.datetime.now() #datetime.datetime.strftime(source['Deadline'], '%m/%d/%y ...')
	other_info = source['Any other relevant information']
	link = source['External link']
	eligibility = source['Eligibility']

	added_by_name = source['Added by']
	if added_by_name not in andrewIDs:
		logging.error('Source #%d was added by %s with unknown Andrew ID, skipping.' % (i, added_by_name))
		return
	added_by_id = andrewIDs[source['Added by']]
	added_by = User.query.filter_by(id=added_by_id).limit(1).first()
	if not added_by:
		added_by = User(added_by_id, admin=True)
		db.session.add(added_by)
		db.session.commit()
		logging.info('Added user %s with known Andrew ID' % added_by_id)

	category_names = list(map(str.strip, source['Category'].split(',')))
	categories = []
	if source['Category'].strip():
		for category_name in category_names:
			category = FundingCategory.query.filter_by(name=category_name).limit(1).first()
			if not category:
				logging.error('Source #%d has invalid category %s, skipping.' % (i, repr(category_name)))
				return
			else:
				categories.append(category)

	sponsor_name = source['Sponsor']
	sponsor = FundingSponsor.query.filter_by(name=sponsor_name).limit(1).first()
	if not sponsor:
		sponsor = FundingSponsor(name=sponsor_name)
		db.session.add(sponsor)
		db.session.commit()
		logging.info('Added sponsor %s' % sponsor_name)

	sexes = []
	schools = []
	years = []
	citizen = False
	independent = True

	parsing_codes = source['Parsing Code'].split(',')
	for parsing_code in parsing_codes:
		if parsing_code == '1':
			sexes.append(1)
		elif parsing_code == '2':
			sexes.append(2)
		elif parsing_code == '10':
			citizen = True
		elif parsing_code == 'F':
			independent = False
		elif parsing_code in fundingSchools.keys():
			schools.append(fundingSchools[parsing_code])
		elif parsing_code in fundingYears.keys():
			years.append(fundingYears[parsing_code])

	if len(sexes) > 1:
		sex = 9
	elif len(sexes) == 1:
		sex = sexes.pop()
	else:
		logging.warning('Source #%d has no sex parsing codes, assuming either sex.' % i)
		sex = 9

	print(sponsor)
	fundingSourceParams = {
		'name': name,
		'application': application,
		'policies': policies,
		'grant_size': grant_size,
		'deadline': deadline,
		'other_info': other_info,
		'link': link,
		'eligibility': eligibility,
		'added_by': added_by,
		'categories': categories,
		'schools': schools,
		'citizen': citizen,
		'independent': independent,
		'sex': sex,
		'years': years,
		'sponsor': sponsor
	}

	source = FundingSource(**fundingSourceParams)

	return source

def read_db(csv_link):
	for code, school in fundingSchools.items():
		fundingSchools[code] = FundingSchool.query.get(school)
	for code, year in fundingYears.items():
		fundingYears[code] = FundingYear.query.filter_by(name=year).limit(1).first()

	r = requests.get(csv_link)
	if r.status_code == 200:
		reader = csv.DictReader(r.text.splitlines())
		sources = []
		for i, source in enumerate(reader):
			source = process_source(i, source)
			sources.append(source)
		return sources
	else:
		return []