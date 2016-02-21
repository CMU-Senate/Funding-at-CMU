import csv
import requests
import datetime
import logging
import io
import iso8601
import collections
import operator
from models import *
from config import db_session

fundingSchoolMappings = {
	'3': 'CFA',
	'4': 'CIT',
	'5': 'MCS',
	'6': 'HSS',
	'7': 'TSB',
	'8': 'BXA',
	'11': 'SCS'
}

fundingYearMappings = {
	'9': 'freshman',
    'A': 'sophomore',
    'B': 'junior',
    'C': 'senior',
    'D': 'graduate'
}

def process_source(i, source, fundingSchools, fundingYears):
	try:
		source_id = int(source['ID'])
	except ValueError:
		logging.error('Source #%d has invalid ID "%s", skipping.' % (i, source['ID']))
		return None, False

	current_source = db_session.query(FundingSource).get(source_id)

	name = source['Name']
	application = source['How to apply']
	policies = source['Policies/Rules']
	grant_size = source['Size of grant/max possible']
	other_info = source['Any other relevant information']
	link = source['External link']
	eligibility = source['Eligibility']

	if not name:
		logging.error('Source #%d has no name, skipping.' % i)

	try:
		deadline_string = source['Deadlines']
		has_time = 'T' in deadline_string
		deadline = iso8601.parse_date(deadline_string)
	except iso8601.iso8601.ParseError:
		logging.error('Source #%d has invalid date "%s", skipping.' % (i, deadline_string))
		return None, 'skipped'

	category_names = list(map(str.strip, source['Category'].split(',')))
	categories = []
	if source['Category'].strip():
		for category_name in category_names:
			category = db_session.query(FundingCategory).filter_by(name=category_name).limit(1).first()
			if not category:
				logging.error('Source #%d has invalid category %s, skipping.' % (i, repr(category_name)))
				return None, 'skipped'
			else:
				categories.append(category)

	sponsor_name = source['Sponsor']
	sponsor = db_session.query(FundingSponsor).filter_by(name=sponsor_name).limit(1).first()
	if not sponsor:
		sponsor = FundingSponsor(name=sponsor_name)
		db_session.add(sponsor)
		db_session.commit()
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

	fundingSourceParams = {
		'id': source_id,
		'name': name,
		'application': application,
		'policies': policies,
		'grant_size': grant_size,
		'deadline': deadline,
		'has_time': has_time,
		'other_info': other_info,
		'link': link,
		'eligibility': eligibility,
		'categories': categories,
		'schools': schools,
		'citizen': citizen,
		'independent': independent,
		'sex': sex,
		'years': years,
		'sponsor': sponsor
	}

	if current_source:
		modified = False
		for param_name, new_val in fundingSourceParams.items():
			current_val = getattr(current_source, param_name)
			if type(new_val) == list:
				if set(map(operator.attrgetter('id'), new_val)) != set(map(operator.attrgetter('id'), current_val)):
					setattr(current_source, param_name, new_val)
					print(set(map(operator.attrgetter('id'), new_val)), set(map(operator.attrgetter('id'), current_val)))
					modified = True
			elif type(new_val) == datetime.datetime:
				if current_val.replace(tzinfo=None) != new_val.replace(tzinfo=None):
					setattr(current_source, param_name, new_val)
					modified = True
			elif current_val != new_val:
				setattr(current_source, param_name, new_val)
				modified = True

		if modified:
			fundingSourceParams['updated_date'] = datetime.datetime.now()
			db_session.commit()
			return current_source, 'updated'
		else:
			return current_source, 'unchanged'
	else:
		fundingSourceParams['added_date'] = datetime.datetime.now()
		source = FundingSource(**fundingSourceParams)
		db_session.add(source)
		db_session.commit()
		return source, 'added'

def read_db(csv_link):
	fundingSchools = dict(map(lambda x: (x[0], db_session.query(FundingSchool).get(x[1])), fundingSchoolMappings.items()))
	fundingYears = dict(map(lambda x: (x[0], db_session.query(FundingYear).filter_by(name=x[1]).limit(1).first()), fundingYearMappings.items()))

	logCaptureString = io.StringIO()
	ch = logging.StreamHandler(logCaptureString)
	ch.setLevel(logging.DEBUG)
	logging.getLogger().addHandler(ch)

	r = requests.get(csv_link)
	if r.status_code == 200:
		reader = csv.DictReader(r.text.splitlines())
		sources = []
		statuses = collections.Counter()
		for i, source in enumerate(reader):
			source, status = process_source(i + 2, source, fundingSchools, fundingYears)
			if source:
				sources.append(source)
			statuses.update([status])

		source_ids = list(map(operator.attrgetter('id'), sources))
		db_sources = list(map(operator.attrgetter('id'), db_session.query(FundingSource).all()))
		for source_id in set(db_sources) - set(source_ids):
			q = db_session.query(FundingSource).filter_by(id=source_id)
			if q.count():
				q.delete()
				statuses.update(['deleted'])
			db_session.commit()

		logString = logCaptureString.getvalue()
		logCaptureString.close()
		logging.getLogger().removeHandler(ch)

		return sources, logString, statuses
	else:
		return [], 'Unable to retrieve CSV (HTTP %s)' % r.status_code
