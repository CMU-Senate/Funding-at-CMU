#!/usr/bin/env python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import subprocess
import sys

app = Flask(__name__)
app.secret_key = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

version = subprocess.check_output(['git', 'describe', '--tags']).decode(sys.stdout.encoding).strip()

db = SQLAlchemy(app)
