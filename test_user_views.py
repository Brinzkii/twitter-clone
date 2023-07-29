"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, Message, User

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

with app.app_context():
    db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            db.session.expire_on_commit = False
            User.query.delete()
            Message.query.delete()

            self.client = app.test_client()

            self.test_user = User.signup(
                username="testuser",
                email="test@test.com",
                password="testuser",
                image_url=None,
            )

            db.session.commit()

    def test_user_signup(self):
        """
        Test user signup route

        GET request - display signup form

        POST request - create new user, login and redirect
        """

        # Testing GET request
        resp = self.client.get("/signup")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Join Warbler today", html)

        # Testing POST request
        resp = self.client.post(
            "/signup",
            data={
                "username": "testuser2",
                "password": "password",
                "email": "testuser@test.com",
                "image_url": "",
            },
            follow_redirects=True,
        )
        html = resp.get_data(as_text=True)

        with app.app_context():
            user = User.query.filter_by(username="testuser2").first()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user.email, "testuser@test.com")
        self.assertIn("@testuser2", html)
        self.assertIn("Log out", html)

    def test_user_login(self):
        """
        Test user login route

        GET request - display signup form

        POST request - login user and redirect to home
        """

        with app.app_context():
            # Testing GET request
            resp = self.client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome back.", html)

            # Testing POST request
            resp = self.client.post(
                "/login",
                data={
                    "username": "testuser",
                    "password": "testuser",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, testuser!", html)
            self.assertIn("Log out", html)

    def test_user_logout(self):
        """Test user logout route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have now been logged out", html)

    def test_user_following(self):
        """Test route for showing a users followed users. If not logged in, should redirect back to home."""

        # Testing while not logged in
        resp = self.client.get(
            f"/users/{self.test_user.id}/following", follow_redirects=True
        )
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)

        # Testing while logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            resp = c.get(f"/users/{self.test_user.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", html)

    def test_user_followers(self):
        """Test route for showing users that follow current user. If not logged in, should redirect back to home."""

        # Testing while not logged in
        resp = self.client.get(
            f"/users/{self.test_user.id}/followers", follow_redirects=True
        )
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)

        # Testing while logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            resp = c.get(f"/users/{self.test_user.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", html)

    def test_user_profile_edit(self):
        """Test route for editing current user profile. If not logged in, should redirect to the login page"""

        # Testing while not logged in
        resp = self.client.get("/users/profile", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("You must be logged in to edit a profile", html)

        # Testing GET request while logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Your Profile", html)

            # Testing POST request while logged in (incorrect password used)
            resp = c.post(
                "/users/profile",
                data={
                    "username": "testuser",
                    "password": "123456",
                    "bio": "This is a test user",
                },
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Incorrect password", html)

            # Testing POST request while logged in
            resp = c.post(
                "/users/profile",
                data={
                    "username": "updatedtestuser",
                    "password": "testuser",
                    "bio": "This is a test user",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@updatedtestuser", html)
            self.assertIn("This is a test user", html)
