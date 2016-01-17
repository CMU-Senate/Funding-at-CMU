#!/usr/bin/env python

import math
from config import app, db, version
from db_init import main
from util import read_db
from flask import render_template, request, redirect, session, abort, flash
from models import *

@app.context_processor
def inject_version():
    return dict(version=version)

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/browse')
    else:
        return render_template('index.html')

@app.route('/browse')
@app.route('/browse/<int:page>')
def browse(page=0):
    if 'user' in session or True:
        page_size = int(request.args.get('page_size', '10'))
        count = FundingSource.query.count()

        context = {
            'page': page,
            'count': count,
            'page_size': page_size,
            'num_pages': math.ceil(count / page_size),
            'sources': FundingSource.query.offset(page * page_size).limit(page_size).all(),
        }
        return render_template('browse.html', **context)
    else:
        abort(401)

@app.route('/admin')
@app.route('/admin/<action>', methods=['GET', 'POST'])
def admin(action=None):
    if not action:
        print(FundingSource.query.count())
        return render_template('admin.html', **{
            'num_sources': FundingSource.query.count() if FundingSource.query else 0
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
        flash('Deleted %s funding sources.' % FundingSource.query.delete())
        db.session.commit()
        return redirect('/admin')
    elif action == 'export':
        pass
    elif action == 'import':
        pass
    else:
        abort(400)

    #main()

if __name__ == '__main__':
    app.run(debug=True) # app.run(host='0.0.0.0')
