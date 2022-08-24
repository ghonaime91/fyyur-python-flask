import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask
app = Flask(__name__)
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config.from_object('config')
from app import controller
