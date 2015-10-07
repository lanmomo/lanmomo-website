import app
import unittest
from models import User
from database import db_session, clear_db

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app.setup('config/default_config.py');

    def tearDown(self):
        clear_db()


class EmailExistsTestCase(BaseTestCase):

    def insert_email_fixture(self):
        username = 'test'
        firstname = 'test'
        lastname = 'test'
        email = 'test@test.com'
        phone = '123-123-1234'
        salt = 'salt'
        password = app.get_hash('test', salt)
        user = User(username, firstname, lastname, email, phone, password, salt)
        db_session.add(user)
        db_session.commit()

    def test_email_does_not_exists(self):
        actual = app.email_exists("test@test.com")
        self.assertFalse(actual)

    def test_email_exists(self):
        self.insert_email_fixture()
        actual = app.email_exists("test@test.com")
        self.assertTrue(actual)



if __name__ == '__main__':
    unittest.main()
