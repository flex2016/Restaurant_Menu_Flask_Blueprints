from project import db
from project.models import Restaurant, User, MenuItem

# create the database and the db table
db.create_all()


# commit the changes
db.session.commit()
