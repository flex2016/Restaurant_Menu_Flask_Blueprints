from app import db
from models.menuItem import MenuItem
from models.restaurant import Restaurant
from models.user import User

# create the database and the db table
db.create_all()


# commit the changes
db.session.commit()
