#!/usr/bin/env python

import math
import io
from config import app, version, login_manager, db_session, engine
from util import read_db
from flask import render_template, request, redirect, session, abort, flash, g
from flask.ext import login
from flask.ext.login import login_required, logout_user
from sqlalchemy import MetaData, desc
from sqlalchemy_utils import escape_like
from sqlalchemy.ext.serializer import loads, dumps
from flask import send_file
from models import *
from db_init import main

@login_manager.user_loader
def load_user(id):
    try:
        return db_session.query(User).get(id)
    except (TypeError, ValueError):
        pass

@app.before_request
def global_user():
    g.user = login.current_user

@app.context_processor
def inject_version():
    return dict(version=version)

@app.context_processor
def inject_user():
    try:
        return {'user': g.user if g.user.is_authenticated else None}
    except AttributeError:
        return {'user': None}

@app.teardown_appcontext
def commit_on_success(error=None):
    if error is None:
        db_session.commit()
    else:
        db_session.rollback()

    db_session.remove()

@app.route('/')
def index():
    if request.args.get('logged_in', False) and g.user and g.user.is_authenticated and not g.user.profile_set:
        return redirect('/profile')
    elif g.user and g.user.is_authenticated:
        return redirect('/browse')
    else:
        return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        context = {
            'schools': db_session.query(FundingSchool).all(),
            'years': db_session.query(FundingYear).all()
        }
        return render_template('profile.html', **context)
    else:
        sex = request.form.get('sex')
        year = request.form.get('year')
        school = request.form.get('school')
        citizen = request.form.get('citizen')

        if sex:
            g.user.sex = int(sex)
        if year:
            g.user.year = db_session.query(FundingYear).get(year)
        if school:
            g.user.school = db_session.query(FundingSchool).get(school)

        g.user.citizen = bool(citizen)

        db_session.commit()

        flash('Profile saved.')
        return redirect('/')

@app.route('/browse')
@app.route('/browse/<int:page>')
@login_required
def browse(page=0):
    page_size = int(request.args.get('page_size', '10'))
    search_query = request.args.get('q', None)
    sex = int(request.args.get('sex', g.user.sex if g.user.sex else '9'))
    citizen = request.args.get('citizen', bool(g.user.citizen))
    sort_order = request.args.get('sort_order', 'title_asc')

    categories = request.args.getlist('categories', None)
    if len(categories) == 1 and ',' in categories[0]:
        categories = categories[0].split(',')
    categories = list(map(int, categories)) if categories else []

    schools = request.args.getlist('schools', None)
    if not schools and not request.args.get('schools_cleared', False) and g.user.school:
        schools = [g.user.school.id]
    elif len(schools) == 1 and ',' in schools[0]:
        schools = schools[0].split(',')

    years = request.args.getlist('years', None)
    if not years and not request.args.get('years_cleared', False) and g.user.year:
        years = [g.user.year.id]
    elif len(years) == 1 and ',' in years[0]:
        years = years[0].split(',')
    years = list(map(int, years)) if years else []

    q = db_session.query(FundingSource)

    if categories:
        q = q.join(FundingSource.categories)
        q = q.filter(FundingCategory.id.in_(categories))

    if schools:
        q = q.join(FundingSource.schools)
        q = q.filter(FundingSchool.id.in_(schools))

    if years:
        q = q.join(FundingSource.years)
        q = q.filter(FundingYear.id.in_(years))

    if search_query:
        parsed_query = escape_like(search_query).replace('_', '__').replace('*', '%').replace('?', '_')
        q = q.join(FundingSource.sponsor)
        q = q.filter(
            FundingSource.name.ilike('%{}%'.format(parsed_query)) |
            FundingSponsor.name.ilike('%{}%'.format(parsed_query))
        )

    if sex and sex in [1, 2]:
        q = q.filter(FundingSource.sex.in_([9, sex]))

    if not citizen:
        q = q.filter(FundingSource.citizen != 1)

    sorts = {
        'title_asc': FundingSource.name,
        'title_desc': desc(FundingSource.name),
        'deadline_nearest': FundingSource.deadline,
        'deadline_farthest': desc(FundingSource.deadline)
    }

    if sort_order in sorts:
        q = q.order_by(sorts[sort_order])
    else:
        q = q.order_by(FundingSource.name)

    count = q.count()

    params = {
        'q': search_query,
        'categories': ','.join(map(str, categories)),
        'years': ','.join(map(str, years)),
        'schools': ','.join(schools),
        'sex': sex,
        'citizen': citizen,
        'sort_order': sort_order
    }
    params = '&'.join(map(lambda x: '%s=%s' % x, filter(lambda x: x[1], params.items())))

    context = {
        'q': search_query,
        'selected_categories': categories,
        'selected_sex': sex,
        'selected_schools': schools,
        'selected_years': years,
        'selected_citizen': citizen,
        'selected_sort_order': sort_order,
        'params': params,
        'page': page,
        'count': count,
        'page_size': page_size,
        'num_pages': math.ceil(count / page_size),
        'sources': q.offset(page * page_size).limit(page_size).all(),
        'categories': db_session.query(FundingCategory).all(),
        'schools': db_session.query(FundingSchool).all(),
        'years': db_session.query(FundingYear).all(),
        'sort_options': [
            ['title_asc', 'Title (A-Z)'],
            ['title_desc', 'Title (Z-A)'],
            ['deadline_nearest', 'Deadline (soonest first)'],
            ['deadline_farthest', 'Deadline (farthest first)'],
        ]
    }
    return render_template('browse.html', **context)

@app.route('/admin')
@app.route('/admin/<action>', methods=['GET', 'POST'])
@login_required
def admin(action=None):
    if g.user and g.user.is_authenticated and g.user.admin:
        if not action:
            return render_template('admin.html', **{
                'num_sources': db_session.query(FundingSource).count() if db_session.query(FundingSource) else 0
            })
        elif action == 'add' and request.method == 'POST':
            spreadsheet_url = request.form.get('spreadsheet_url')
            if not spreadsheet_url:
                abort(400)
            else:
                sources = read_db(spreadsheet_url)
                flash('Added %s funding sources.' % len(list(filter(bool, sources))))
                return redirect('/admin')
        elif action == 'delete':
            flash('Deleted %s funding sources.' % db_session.query(FundingSource).delete())
            db_session.commit()
            return redirect('/admin')
        elif action == 'export':
            export = io.BytesIO(dumps(db_session.query(FundingSource).all()))
            return send_file(export, attachment_filename='funding.db', as_attachment=True)
        elif action == 'import':
            import_file = request.files['import'].read()
            sources = loads(import_file, MetaData(bind=engine), db_session)
            for source in sources:
                db_session.merge(source)
            flash('Merged %s funding sources.' % len(sources))
            return redirect('/admin')
        else:
            abort(400)
    elif g.user and g.user.is_authenticated:
        abort(403)
    else:
        abort(401)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0')
