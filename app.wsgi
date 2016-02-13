#!/usr/bin/python3

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/funding.cmu.edu/')

from app import app as application
application.secret_key = 'a1de944a2c27489e925674eb3ae4fb4ad83bb617794057f5002e39a406f724c05ad1856f'
