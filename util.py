import csv
import requests
import datetime
import logging
from models import User, FundingCategory, FundingSchool, FundingYear, FundingSponsor
from config import db

andrewIDs = {
	'Michael': 'mcgormle',
	'Aashir': 'amaster',
	'Jeannie': 'jemichae',
	'Nadia': 'nrazek',
	'Shelly': 'sbalassy',
	'Stephanie': 'semore'
}

def process_source(i, source):
	name = source['Name']
	application = source['How to apply']
	policies = source['Policies/Rules']
	grant_size = source['Size of grant/max possible']
	#deadline = datetime.datetime.strftime(source['Deadline'], '%m/%d/%y')
	other_info = source['Any other relevant information']
	link = source['External link']

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

	parsing_codes = source['Parsing Code'].split(',')

	return source

def read_db(csv_link):
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