""" Message model tests."""

# run these tests like:
#
#  FLASK_ENV=production python3 -m unittest test_set_model.py


import os
from unittest import TestCase

from models import db, User, Set, Verse

# BEFORE we import our app, set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///mtword_test"

# Now we can import app

from project import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class SetModelTestCase(TestCase):
    """Test model for sets."""

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
            user_id=u1.id,
            created_at=None,
        )

        db.session.add(set1)
        db.session.commit()

        u1.sets.append(set1)
        db.session.commit()

        # Set2 that is favorited by the user
        set2 = Set(
            name="testset2",
            description="description2",
            user_id=u1.id,
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

    def test_set_repr(self):
        """ Test that the set is being represented correctly """
        my_set = Set.query.get(self.set1Id)

        self.assertEqual(repr(my_set), f"<Set {self.name} by {self.user.first_name} \
            {self.user.last_name}>")

    def test_set_relationship_with_user(self):
        """ Test that the relationship between set and user is \
            correctly established
        """

        test_user1 = Set.query.get(self.u1Id)
        my_set = Set.query.get(self.set1Id)

        self.assertEqual(test_user1, my_set.user)
        self.assertEqual(len(test_user1.sets), 2)

        set3 = Set(
            name="testset3",
            description="description3",
        )

        test_user1.sets.append(set3)
        db.session.commit()

        # Test that test_user1.sets is a list containing my_set and set3?
        self.assertEqual(len(test_user1.sets), 3)
        self.assertIn(my_set, test_user1.sets)
        self.assertIn(set3, test_user1.sets)

    def test_set_relationship_with_verse(self):
        """ Test that the relationship between set and verse is
            correctly established
        """

        my_set = Set.query.get(self.set1Id)
        verse1 = Verse.query.get(self.v1Id)
        verse2 = Verse.query.get(self.v2Id)

        self.assertIn(verse1, my_set.verses)
        self.assertIn(verse2, my_set.verses)

        verse3 = Verse(
            reference="ref3",
            verse="v3"
        )

        my_set.verses.append(verse3)
        db.session.commit()

        self.assertEqual(len(my_set.verses), 3)
        self.assertIn(verse3, my_set.verses)
