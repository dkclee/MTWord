"""User model tests."""

# run these tests like:
#
#  FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, InvalidRequestError, IntegrityError

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test the model for the User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u)
        db.session.commit()

        self.u1 = u
        self.u2 = u2

        self.client = app.test_client()
    
    def tearDown(self):
        """ Clean up test database """

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        # Try to test what the actual data structure is ([]): 
        # Nibbling (testing a small part)
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

        self.assertEqual(len(self.u2.messages), 0)
        self.assertEqual(len(self.u2.followers), 0)

        # Testing that the user is displayed correctly
        # Make the f-strings a separate variable?
        self.assertEqual(repr(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")
        self.assertEqual(repr(self.u2), f"<User #{self.u2.id}: {self.u2.username}, {self.u2.email}>")

    def test_follow_unfollow(self):
        """ Test the following and unfollowing functionality """

        self.u1.following.append(self.u2)

        db.session.commit()

        # User 1 is following user 2, user 2 is followed by user 1
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u1.is_followed_by(self.u2))

        self.assertFalse(self.u2.is_following(self.u1))
        self.assertTrue(self.u2.is_followed_by(self.u1))

        self.u1.following.remove(self.u2)

        db.session.commit()

        # User 1 is not following user 2, user 2 is not followed by user 1
        self.assertFalse(self.u1.is_following(self.u2))
        self.assertFalse(self.u1.is_followed_by(self.u2))

        self.assertFalse(self.u2.is_following(self.u1))
        self.assertFalse(self.u2.is_followed_by(self.u1))
    
    def test_sign_up_success(self):
        """ Test signing up a user with valid credentials """

        # Is there a way to make this a separate helper function?
        user = User.signup(
            username="new_user",
            email="new_email@email.com",
            password="password",
            image_url="http://google.com",
        )

        db.session.commit()

        # Try to test the entire instance instead of indv properties
        self.assertEqual(user.username, "new_user")
        self.assertEqual(user.email, "new_email@email.com")
        self.assertEqual(user.image_url, "http://google.com")

    def test_sign_up_failure(self):
        """ Test signing up a user with invalid credentials
            (invalid when some fields are left null or not unique) """

        # Not unique username (Integrity Error)
        try:
            invalid_user = User.signup(
                username="testuser",
                email="new_email@email.com",
                password="password",
                image_url="http://google.com",
            )

            db.session.commit()
            # We can use self.assertRaises

            self.assertTrue(False)

        except IntegrityError:

            db.session.rollback()
            
            self.assertTrue(True)

        # Null Email (IntegrityError) 
        # Note: As long as we rollback after IntegrityError, we will
        # not get an InvalidRequestError
        try:
            invalid_user2 = User.signup(
                username="testuser4",
                email=None,
                password="password",
                image_url="http://google.com",
            )

            db.session.commit()

            self.assertTrue(False)

        except IntegrityError:

            self.assertTrue(True)


    def test_authenticate_success(self):
        """ Test authenticating a user with valid credentials """
        user = User.signup(
            username="new_user",
            email="new_email@email.com",
            password="password",
            image_url="http://google.com",
        )
        db.session.commit()

        # Helper function?
        found_user = User.authenticate(
            username=user.username,
            password="password"
        )

        self.assertTrue(found_user)
        self.assertEqual(found_user.username, "new_user")
        self.assertEqual(found_user.email, "new_email@email.com")
        self.assertEqual(found_user.image_url, "http://google.com")

    def test_authenticate_failure(self):
        """ Test authenticating a user with invalid credentials
        
        invalid when username doesn't exist or password incorrect for user
        """
        user = User.signup(
            username="new_user",
            email="new_email@email.com",
            password="password",
            image_url="http://google.com",
        )
        db.session.commit()

        failed_to_find = User.authenticate(
            username="wrong_username",
            password="password"
        )

        self.assertFalse(failed_to_find)

        failed_again = User.authenticate(
            username="new_user",
            password="wrong_password"
        )

        self.assertFalse(failed_again)
