from app import db
from models.restaurant import Restaurant
from models.user import User


class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship(Restaurant)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)


    def __init__(self, name, description, price, course, restaurant_id, user_id):
      self.name = name
      self.description = description
      self.price = price
      self.course = course
      self.restaurant_id = restaurant_id
      self.user_id = user_id



    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }
