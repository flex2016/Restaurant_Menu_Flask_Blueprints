from project import app
import unittest

class FlaskTestCase(unittest.TestCase):


    def test_restaurant(self):
        tester = app.test_client(self)
        response = tester.get('/restaurant/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_restaurant_new(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/new/',
            data=dict(id=10, name="Pizza Place"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Created', response.data)

    def test_restaurant_edit(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/15/edit/',
            data=dict(name="FLEX"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Edited', response.data)

    def test_restaurant_delete(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/16/delete/',
            data=dict(name=""),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Deleted', response.data)

    def test_showMenu(self):
        tester = app.test_client(self)
        response = tester.get('/restaurant/3/menu/', content_type='html/text')
        self.assertTrue(b'Add Menu Item' in response.data)

    def test_newMenuItem(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/19/menu/new/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree",restaurant_id="1", user_id="1"),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Created', response.data)

    def test_editMenuItem(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/19/menu/51/edit/',
            data=dict(name="New Pizza", description="Cheese Pizza", price="12.99", course="Entree"),
            follow_redirects=True
        )
        self.assertIn(b'Menu Item Successfully Edited', response.data)

    def test_deleteMenuItem(self):
        tester = app.test_client()
        response = tester.post(
            '/restaurant/19/menu/52/delete/',
            data=dict(name=""),
            follow_redirects=True
        )
        self.assertIn(b'Successfully Deleted', response.data)



if __name__ == '__main__':
    unittest.main()
