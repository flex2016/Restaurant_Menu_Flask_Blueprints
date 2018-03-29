from flask import Flask
from flask_sqlalchemy import SQLAlchemy



# create the application object
app = Flask(__name__)
# config
app.secret_key = 'my precious'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:flex@localhost/restaurants'

# create the sqlalchemy object
db = SQLAlchemy(app)

# import db schema
from models.menuItem import MenuItem
from models.restaurant import Restaurant
from models.user import User


if __name__ == '__main__':
    app.run(port=5000, debug=True)
