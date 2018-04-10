from project import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from lib.sql import ResourceMixin


# class ResourceMixin(object):

#     def save(self):
#         """
#         Save a model instance.

#         :return: Model instance
#         """
#         db.session.add(self)
#         db.session.commit()

#         return self

#     def delete(self):
#         """
#         Delete a model instance.

#         :return: db.session.commit()'s result
#         """
#         db.session.delete(self)
#         return db.session.commit()


class User(ResourceMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))
    restaurant = db.relationship('Restaurant', backref='restaurant')
    menuItems = db.relationship('MenuItem', backref='user')

    def __init__(self, name, email, picture):
        self.name = name
        self.email = email
        self.picture = picture


class Restaurant(ResourceMixin, db.Model):
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


class MenuItem(ResourceMixin, db.Model):
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
