"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config["DEBUG_TB_ENABLED"] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.testuser_id = self.testuser.id
        self.testuser2_id = self.testuser2.id

        msg1 = Message(text="Deleting you", user_id=self.testuser_id)
        db.session.add(msg1)
        db.session.commit()

        msg2 = Message(text="Hi", user_id=self.testuser2_id)

        db.session.add(msg2)
        db.session.commit()

        self.testmsg1_id = msg1.id
        self.testmsg2_id = msg2.id

    def tearDown(self):

        db.session.rollback()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg2 = Message.query.filter_by(text="Hello").one()
            self.assertEqual(msg2.text, "Hello")

    def test_delete_message(self):
        """Can user delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # resp = c.post("/messages/new", data={"text": "Hello"})

            # msg = Message.query.one()

            # self.assertEqual(msg.text, "Hello")

            msg = Message.query.get(self.testmsg1_id)
            resp = c.post(f"/messages/{self.testmsg1_id}/delete", follow_redirects=True)

            user1 = User.query.get(self.testuser_id)

            self.assertNotIn(msg, user1.messages)

    def test_delete_other_user_message(self):
        """Can user delete a message belonging to another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{self.testmsg2_id}/delete")

            self.assertEqual(resp.status_code, 401)
    
    def test_show_message(self):
        """Can user see a specific message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get(f"/messages/{self.testmsg2_id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="messages"', html)
    
    def test_when_logged_out_fails(self):
        """ Can user do the following when logged out: add, delete, messages? """
        
        with self.client as c:
            
            # Add?
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="not-logged-in-message"', html)
            self.assertIn("Access unauthorized.", html)

            # Delete?
            resp = c.post(f"/messages/{self.testmsg2_id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="not-logged-in-message"', html)
            self.assertIn("Access unauthorized.", html)
