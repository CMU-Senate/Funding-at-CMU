#!/usr/bin/env python

from config import app
from db_init import main
from util import read_db

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/admin')
def admin():
    main()
    return repr(read_db('https://docs.google.com/spreadsheets/d/1njc8zi2gVvmtCzISVtay2pQYzkNij73jbfGwUS8l7A0/pub?gid=0&single=true&output=csv'))

if __name__ == '__main__':
    app.run(debug=True) # app.run(host='0.0.0.0')