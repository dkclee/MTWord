"""User model tests."""

# run these tests like:
#
#  FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase

from flask import IntegrityError

from flask_bcrypt import Bcrypt

from models import db, User, Set, Verse

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///bible_memorization_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

bcrypt = Bcrypt()


class UserModelTestCase(TestCase):
    """Test the model for the User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Set.query.delete()
        Verse.query.delete()

        u1 = User(
            first_name="fn1",
            last_name="ln1",
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        db.session.add(u1)
        db.session.commit()

        verse1 = Verse(
            reference="ref1",
            verse='v1'
        )

        verse2 = Verse(
            reference="ref2",
            verse="v2"
        )

        db.session.add(verse1, verse2)
        db.session.commit()

        # Set 1 belonging to a user
        set1 = Set(
            name="testset1",
            description="description1",
        )

        u1.sets.append(set1)

        db.session.commit()

        # Set2 that is favorited by the user
        set2 = Set(
            name="testset2",
            description="description2",
        )

        u1.sets.append(set2)
        u1.favorites.append(set2)

        db.session.commit()

        # Add the verses to the set
        set1.verses = [verse1, verse2]

        db.session.commit()

        # Put user, set and verse ids on self
        self.u1Id = u1.id
        self.set1Id = set1.id
        self.set2Id = set2.id
        self.v1Id = verse1.id
        self.v2Id = verse2.id

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up test database """

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u1 = User.query.get(self.u1Id)

        u2 = User(
            first_name="fn2",
            last_name="ln2",
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u2)
        db.session.commit()

        # User should have no sets upon creation
        self.assertEqual(len(u2.sets), 0)

        # Testing that the user is displayed correctly
        self.assertEqual(repr(u1), f"<User {u1.full_name}>")
        self.assertEqual(repr(u2), f"<User {u2.full_name}>")

    def test_update_password(self):
        """ Test updating the password functionality """

        u1 = User.query.get(self.u1Id)

        u1.update_password("newPWd1")

        self.assertTrue(bcrypt.check_password_hash(u1.password, "newPWd1"))

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
        with self.assertRaises(IntegrityError):
            invalid_user = User.register(
                first_name="fn1",
                last_name="ln1",
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD1"
            )

            db.session.commit()

        db.session.rollback()  # To avoid the InvalidRequestError

        # Null Email (IntegrityError)
        with self.assertRaises(IntegrityError):
            invalid_user2 = User.register(
                first_name="fn2",
                last_name="ln2",
                email=None,
                username="testuser2",
                password="HASHED_PASSWORD2"
            )

            db.session.commit()

        db.session.rollback()

    def test_authenticate_success(self):
        """ Test authenticating a user with valid credentials """
        user = User.register(
            first_name="fn_new",
            last_name="ln_new",
            username="new_user",
            email="new_email@email.com",
            password="password"
        )
        db.session.commit()

        # Helper function?
        found_user = User.authenticate(
            username=user.username,
            password="password"
        )

        self.assertTrue(found_user)
        self.assertEqual(found_user.first_name, "fn_new")
        self.assertEqual(found_user.last_name, "ln_new")
        self.assertEqual(found_user.username, "new_user")
        self.assertEqual(found_user.email, "new_email@email.com")

    def test_authenticate_failure(self):
        """ Test authenticating a user with invalid credentials

        invalid when username doesn't exist or password incorrect for user
        """
        user = User.register(
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
