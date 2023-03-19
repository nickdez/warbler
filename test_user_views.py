"""User Views tests."""

import os
from unittest import TestCase

from models import db, Message, User, Likes
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser_id = 2294
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("Nick", "test1@test.com", "password", None)
        self.u1_id = 123
        self.u1.id = self.u1_id
        self.u2 = User.signup("Ryan", "test2@test.com", "password", None)
        self.u2_id = 456
        self.u2.id = self.u2_id
        self.u3 = User.signup("Kirsten", "test3@test.com", "password", None)
        self.u4 = User.signup("Jamie", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    
    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@Nick", str(resp.data))
            self.assertIn("@Ryan", str(resp.data))
            self.assertIn("@Kirsten", str(resp.data))
            self.assertIn("@Jamie", str(resp.data))
    
    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@Jamie", str(resp.data))            

            self.assertNotIn("@Nick", str(resp.data))
            self.assertNotIn("@Ryan", str(resp.data))
            self.assertNotIn("@Kirsten", str(resp.data))
    
    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
    
    def setup_likes(self):
        msg1 = Message(text="test text 1", user_id=self.testuser_id)
        msg2 = Message(text="test text 2", user_id=self.testuser_id)
        msg3 = Message(id=2294, text="test text 3", user_id=self.u1_id)
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()

        l1 = Likes(user_id=self.testuser_id, message_id=2294)

        db.session.add(l1)
        db.session.commit()
    
    def test_user_show_with_likes(self):
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)
    
    def test_show_following(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@Nick", str(resp.data))
            self.assertIn("@Ryan", str(resp.data))
            self.assertNotIn("@Kirsten", str(resp.data))
            self.assertNotIn("@testing", str(resp.data))
    
    def test_show_followers(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@Nick", str(resp.data))
            self.assertNotIn("@Ryan", str(resp.data))
            self.assertNotIn("@Kirsten", str(resp.data))
            self.assertNotIn("@testing", str(resp.data))
    
    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@Nick", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_unauthorized_followers_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@Nick", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
            