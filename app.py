#!/usr/bin/env python

import math
import io
from config import app, version, login_manager, db_session, engine
from util import read_db
from flask import render_template, request, redirect, session, abort, flash, g
from flask.ext import login
from flask.ext.login import login_required, logout_user
from sqlalchemy import MetaData
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
        gender = request.form.get('gender')
        year = request.form.get('year')
        school = request.form.get('school')
        print(gender, year, school)

        flash('Profile saved.')
        return render_template('profile.html', **context)


@app.route('/browse')
@app.route('/browse/<int:page>')
@login_required
def browse(page=0):
    page_size = int(request.args.get('page_size', '10'))
    search_query = request.args.get('q', None)
    category = request.args.get('category', None)

    q = db_session.query(FundingSource)

    if category:
        q = db_session.query(FundingCategory).get(int(category)).sources

    if search_query:
        title_query = escape_like(search_query).replace('_', '__').replace('*', '%').replace('?', '_')
        q = q.filter(FundingSource.name.ilike('%{}%'.format(title_query)))

    count = q.count()

    params = {
        'q': search_query,
        'category': category
    }
    params = '&'.join(map(lambda x: '%s=%s' % x, filter(lambda x: x[1], params.items())))

    context = {
        'q': search_query,
        'category': category,
        'params': params,
        'page': page,
        'count': count,
        'page_size': page_size,
        'num_pages': math.ceil(count / page_size),
        'sources': q.offset(page * page_size).limit(page_size).all(),
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
