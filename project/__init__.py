#################
#### imports ####
#################


from flask import Flask, render_template, session, request, redirect, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os


################
#### config ####
################

# create the application object
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
# create the sqlalchemy object
db = SQLAlchemy(app)
# import db schema
from models import Restaurant, User, MenuItem
from project.home.views import home_blueprint
from project.user.views import user_blueprint

# register our blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(user_blueprint)
