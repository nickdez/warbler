"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app



# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data. - IMPLEMENTED"""

        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "user1@test.com", "password", None)
        uid1 = 111
        u1.id = uid1

        u2 = User.signup("user1", "user2@test.com", "password", None)
        uid2 = 222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1
        
        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    ###User following tests###


    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following),1)
        self.assertEqual(len(self.u1.followers),0)
        self.assertEqual(len(self.u2.followers),1)
        self.assertEqual(len(self.u1.following),0)

        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)
    
    def test_is_following(self):

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))
    
    def test_is_followed_by(self):

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
    
### SIGNUP TESTS ###

    def test_valid_signup(self):

        user_test = User.signup("testname", "test@test.com", "password", None)
        uid = 1111
        user_test.id = uid
        db.session.commit()

        user_test = User.query.get(uid)
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username("testname"))
        self.assertEqual(user_test.email("test@test.com"))
        self.assertNotEqual(user_test.password("password"))
        self.assertTrue(user_test.password.startswith("$2bn$"))

    def test_invalid_username_signup(self):

        invalid = User.signup("None", "test@test.com", "password", None)
        uid = 2294
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_signup(self):

        invalid = User.signup("Nick123", None , "password", None)
        uid = 2295
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
   
    def test_invalid_password_signup(self):

        invalid = User.signup("Nick123", "test@test.com" , None , None)
        uid = 2296
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

####Authentication Tests####

    def test_valid_authenticate(self):

        n = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(n)
        self.assertEqual(n.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("wrongusername", "password"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))







    
   
