#!/usr/bin/env python

import math
from config import app
from db_init import main
from util import read_db
from flask import render_template, request, redirect, session
from models import *

@app.route('/')
def index():
    if 'user' in session or True:
        return redirect('/browse')
    else:
        return render_template('index.html')

@app.route('/browse')
@app.route('/browse/<int:page>')
def browse(page=0):
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

@app.route('/admin')
def admin():
    return render_template('admin.html')
    #main()
    #return repr(read_db('https://docs.google.com/spreadsheets/d/1njc8zi2gVvmtCzISVtay2pQYzkNij73jbfGwUS8l7A0/pub?gid=0&single=true&output=csv'))

if __name__ == '__main__':
    app.run(debug=True) # app.run(host='0.0.0.0')
