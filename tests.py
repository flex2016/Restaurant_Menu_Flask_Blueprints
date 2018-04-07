import unittest
from flask.ext.testing import TestCase
from project import app, db
from project.models import Restaurant, User, MenuItem



class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        # db.session.add(BlogPost("Test post", "This is a test. Only a test."))
        # db.session.add(User("admin", "ad@min.com", "admin"))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()



class FlaskTestCase(BaseTestCase):


    def test_restaurant(self):

        response = self.client.get('/restaurant/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_restaurant_new(self):

        response = self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Created', response.data)

    def test_restaurant_edit(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        response=self.client.post(
            '/restaurant/1/edit/',
            data=dict(name="New Pizza 201"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Edited', response.data)

    def test_restaurant_delete(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        response = self.client.post(
            '/restaurant/1/delete/', follow_redirects=True)

        self.assertIn(b'Successfully Deleted', response.data)

    def test_showMenu(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        self.client.post(
            '/restaurant/1/menu/new/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        response = self.client.get('/restaurant/1/menu/', content_type='html/text')
        self.assertTrue(b'Add Menu Item' in response.data)

    def test_newMenuItem(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        response = self.client.post(
            '/restaurant/1/menu/new/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Created', response.data)

    def test_editMenuItem(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        self.client.post(
            '/restaurant/1/menu/new/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        response = self.client.post(
            '/restaurant/1/menu/1/edit/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        self.assertIn(b'Menu Item Successfully Edited', response.data)

    def test_deleteMenuItem(self):
        self.client.post(
            '/restaurant/new/',
            data=dict(name="Pizza Place"),
            follow_redirects=True
        )
        self.client.post(
            '/restaurant/1/menu/new/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        response = self.client.post(
            '/restaurant/1/menu/1/delete/',
            follow_redirects=True
        )
        self.assertIn(b'Successfully Deleted', response.data)



if __name__ == '__main__':
    unittest.main()
