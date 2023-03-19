"""User Message tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app



db.create_all()

class UserMessageTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.uid = 9422
        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        
        msg = Message(
            text="Warbler test",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()


        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "Warbler test")
    
    def test_message_likes(self):
        msg1 = Message(
            text="Hello world",
            user_id=self.uid
        )

        msg2 = Message(
            text="Welcome to Warbler",
            user_id=self.uid 
        )

        u = User.signup("somanytests", "test@email.com", "password", None)
        uid = 420
        u.id = uid
        db.session.add_all([msg1, msg2, u])
        db.session.commit()

        u.likes.append(msg1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, msg1.id)
