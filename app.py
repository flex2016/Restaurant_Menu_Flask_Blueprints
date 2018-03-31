from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy



# create the application object
app = Flask(__name__)


# config
import os
app.config.from_object(os.environ['APP_SETTINGS'])

# create the sqlalchemy object
db = SQLAlchemy(app)


# import db schema
from models import *


# Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    # restaurants = Restaurant.query.all()
    restaurants = db.session.query(Restaurant).order_by(Restaurant.name.asc())
    return render_template('publicrestaurants.html', restaurants=restaurants)


if __name__ == '__main__':

    app.run(port=5000)
