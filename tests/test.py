import unittest
from flask_testing import TestCase
from Question import app
from Question import db

class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        #db.session.add(User("admin", "ad@min.com", "admin"))
        #db.session.add(
         #   BlogPost("Test post", "This is a test. Only a test.", "admin"))
        #db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    # Ensure that Flask was set up correctly
    def test_index(self):
        response = self.client.get('/login/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        response = self.client.get('/login/')
        self.assertIn(b'Log In', response.data)

    # Ensure login behaves correctly with correct credentials
    def test_correct_login(self):
        response = self.client.post(
            '/login/',
            data=dict(email="test@hotmail.com", password="test"),follow_redirects=True)
        self.assertIn(b'Questions', response.data)

    #Ensure can not login with wrong credentials
    def test_incorrect_login(self):
        response = self.client.post(
            '/login/',
            data=dict(email="wrong", password="wrong"),follow_redirects=True)
        self.assertIn(b'Email', response.data)

#Ensure Log out route
    def test_logout_route_requires_login(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'Log In', response.data)

         # Ensure that posts show up on the main page
    def test_posts_show_up_on_main_page(self):
        response = self.client.post(
            '/login',
            data=dict(email="test@hotmail.com", password="test"),
            follow_redirects=True
        )
        self.assertIn(b'This is a Question', response.data)



if __name__ == '__main__':
    unittest.main()