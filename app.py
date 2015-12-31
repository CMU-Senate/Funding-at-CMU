#!/usr/bin/env python

from config import app
import models
from db_init import main

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/admin')
def admin():
    #main()
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True) # app.run(host='0.0.0.0')