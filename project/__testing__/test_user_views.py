"""User views tests."""

# run these tests like:
#
#  FLASK_ENV=production python -m unittest test_user_views.py


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

app.config["WTF_CSRF_ENABLED"] = False
app.config["DEBUG_TB_ENABLED"] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Test views for the user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="PASSWORD",
            image_url="http://google.com",
        )

        db.session.commit()

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="PASSWORD2",
            image_url="http://google.com",
        )

        db.session.commit()

        self.u1_username = u.username
        self.u2_username = u2.username
        self.u1_id = u.id
        self.u2_id = u2.id
        self.u2_email = u2.email

        self.client = app.test_client()

        self.login_data = {
            "username": self.u1_username,
            "password": "PASSWORD"
        }
    
    def tearDown(self):
        """ Clean up test database """

        db.session.rollback()

    def test_login_success(self):
        """ Test that the login form correctly displays and
            user with valid credentials can log in """

        resp = self.client.get("/login")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)

        login_data = {
            "username": self.u1_username,
            "password": "PASSWORD"
        }

        resp = self.client.post("/login", data=login_data, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'Hello, {self.u1_username}!', html)
        self.assertIn(f'@{self.u1_username}', html)
    
    def test_login_failure(self):
        """ Test processing login form with invalid credentials shows form 
        again with errors 
        """

        wrong_username_data = {
            "username": "ooops",
            "password": "PASSWORD"   
        }
        resp = self.client.post("/login", data=wrong_username_data, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Invalid credentials.", html)

        wrong_password_data = {
            "username": self.u1_username,
            "password": "OOOOPS"
        }

        resp = self.client.post("/login", data=wrong_password_data, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Invalid credentials.", html)

        wrong_data = {
            "username": "does_not_exist",
            "password": "OOOOPS"
        }

        resp = self.client.post("/login", data=wrong_data, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Invalid credentials.", html)
    
    def test_list_users(self):
        """ Test users page shows correct HTML indexing users info
        
        Also test that search function shows correct users matching search term
         """

        resp = self.client.get("/users")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!-- Index page showing list of users  -->", html)


        resp = self.client.get("/users?q=testuser2")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!-- Index page showing list of users  -->", html) # Try to test using id's
        self.assertIn("@testuser2", html)
    
    def test_show_user(self):
        """ Test user profile page shows correct information about that user """

        resp = self.client.get(f"/users/{self.u1_id}")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f"@{self.u1_username}", html)
        self.assertIn('id="messages"', html)
        self.assertIn('id="warbler-hero"', html)
        self.assertIn("<!-- User detail messages here -->", html)
        

    def test_show_user_following_failure(self):
        """ Test that if not logged in, redirects to home page with error message
        """

        resp = self.client.get(f"/users/{self.u1_id}/following", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

    def test_show_user_following_success(self):
        """ Test that list of user's details are displayed if the logged in 
        user at user_id follows them         
        """

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.get(f"/users/{self.u1_id}/following")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="following', html)
        self.assertIn(f"@{self.u1_username}", html)
        self.assertIn('id="warbler-hero"', html)

    def test_show_user_followers_failure(self):
        """ Test that if not logged in, redirects to home page with error message
        """

        resp = self.client.get(f"/users/{self.u1_id}/followers", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

    def test_show_user_followers_success(self):
        """ Test that list of user's followers are shown when the user is 
            logged in"""

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.get(f"/users/{self.u1_id}/followers", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="followers"', html)
        self.assertIn(f"@{self.u1_username}", html)
        self.assertIn('id="warbler-hero"', html)

    def test_add_follow_failure(self):
        """ Test to try to follow without logging in
            redirects to home page with error message"""

        resp = self.client.post(f"/users/follow/{self.u1_id}", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

        # You cannot follow yourself
        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.post(f"/users/follow/{self.u1_id}", 
                                follow_redirects=True,
                                headers={
                                    "Referer": '/'
                                })
        html = resp.get_data(as_text=True)

        user = User.query.get(self.u1_id)
        self.assertNotIn(user, user.followers)
        self.assertIn("You cannot follow yourself.", html)

    def test_add_follow_success(self):
        """ Test to try to follow while logged in (follow a different user)
            redirected to the the page you were in with the user followed"""

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.post(f"/users/follow/{self.u2_id}",
                                follow_redirects=True,
                                headers={
                                    "Referer": '/'
                                })

        html = resp.get_data(as_text=True)

        user1 = User.query.get(self.u1_id)

        user2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(user1, user2.followers)
        self.assertIn(f"Successfully followed user: {user2.username}", html)
    
    def test_stop_follow_failure(self):
        """ Test to try to unfollow without logging in
            redirects to home page with error message """

        resp = self.client.post(f"/users/stop-following/{self.u1_id}", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

        # You cannot unfollow yourself
        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.post(f"/users/stop-following/{self.u1_id}", 
                                follow_redirects=True,
                                headers={
                                    "Referer": '/'
                                })
        html = resp.get_data(as_text=True)

        user = User.query.get(self.u1_id)
        self.assertNotIn(user, user.followers)
        self.assertIn("You cannot unfollow yourself.", html)

    def test_stop_follow_success(self):
        """ Test that unfollowing user you were following while logged in
            will redirect to the page you were in with the user unfollowed"""

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        self.client.post(f"/users/follow/{self.u2_id}",
                                follow_redirects=True,
                                headers={
                                    "Referer": '/'
                                })
        
        resp = self.client.post(f"/users/stop-following/{self.u2_id}",
                                follow_redirects=True,
                                headers={
                                    "Referer": '/'
                                })
        html = resp.get_data(as_text=True)

        user1 = User.query.get(self.u1_id)

        user2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(user1, user2.followers)
        self.assertIn(f"Successfully unfollowed user: {user2.username}", html)


    def test_show_profile_edit_form_success(self):
        """ Test that route to profile shows edit form for logged in user  """

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        resp = self.client.get("/users/profile")        
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)

    def test_show_profile_edit_form_failure(self):
        """ Test that if not logged in, redirects to home page with error message
        """

        resp = self.client.get(f"/users/profile", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

    def test_edit_profile_success(self):
        """ Test that editing profile with valid inputs redirects to user show page
         with success message      
        """

        self.client.post("/login", data=self.login_data, follow_redirects=True)

        edit_data = {
            "username": self.u1_username,
            "password": "PASSWORD",
            "email": "new-email@test.com"
        }
        resp = self.client.post(f"/users/profile", data=edit_data, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!-- User detail messages here -->", html)
        self.assertIn(f"@{self.u1_username}", html)
        self.assertIn('id="warbler-hero"', html)
        self.assertIn(f"Successfully updated: {self.u1_username}", html)

    def test_edit_profile_failure(self):
        """ Test that editing profile with invalid inputs renders edit form again with error
        messages  """

        self.client.post("/login", data=self.login_data, follow_redirects=True)
    
        duplicate_username_data = {
            "username": self.u2_username,
            "password": "PASSWORD",
            "email": "new-email@test.com"
        }

        resp = self.client.post("/users/profile", 
                                data=duplicate_username_data, 
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Username is taken.", html)

        dup_email_data = {
            "username": self.u1_username,
            "password": "PASSWORD",
            "email": self.u2_email
        }

        resp = self.client.post("/users/profile", 
                                data=dup_email_data, 
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Email is taken.", html)

        wrong_pw_data = {
            "username": self.u1_username,
            "password": "WRONGGGGG",
            "email": "new-email@test.com"
        }

        resp = self.client.post("/users/profile", 
                                data=wrong_pw_data, 
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("Password is incorrect.", html)

    def test_delete_user_success(self):
        """ Test that deleting a user while logged in is successful and redirect to
            signup page"""

        self.client.post("/login", data=self.login_data, follow_redirects=True)
        
        resp = self.client.post("/users/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user_form"', html)
        self.assertIn("User has been deleted successfully", html)

    def test_delete_user_failure(self):
        """ Test that deleting a user fails if not logged in 
            Go to the homepage
        """

        resp = self.client.post("/users/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="not-logged-in-message"', html)
        self.assertIn("Access unauthorized.", html)

