from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey




class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))
    restaurant = db.relationship('Restaurant', backref='restaurant')
    menuItems = db.relationship('MenuItem', backref='user')

    def __init__(self, name,email, picture):
      self.name = name
      self.email = email
      self.picture = picture


class Restaurant(db.Model):
    __tablename__ = 'restaurant'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    menuItem = db.relationship('MenuItem', backref='menu_item')



    def __init__(self, name, user_id):
      self.name = name
      self.user_id = user_id



    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



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
