"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()


class UserModelTestCase(TestCase):
    """Test models for users."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()

            db.session.commit()

            self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():
            u1 = User(
                email="test1@test.com", username="testuser1", password="HASHED_PASSWORD"
            )

            db.session.add(u1)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u1.messages), 0)
            self.assertEqual(len(u1.followers), 0)

    def test_is_followed_by(self):
        """Should take two users and return whether the first is followed by the second"""

        with app.app_context():
            u1 = User(
                email="test1@test.com", username="testuser1", password="HASHED_PASSWORD"
            )
            u2 = User(
                email="test2@test.com", username="testuser2", password="HASHED_PASSWORD"
            )

            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()

            f = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)

            db.session.add(f)
            db.session.commit()

            # User 1 should be followed by user 2
            self.assertTrue(User.is_followed_by(u1, u2))
            self.assertFalse(User.is_followed_by(u2, u1))

    def test_is_following(self):
        """Should take two users and return whether the first is following the second"""

        with app.app_context():
            u1 = User(
                email="test1@test.com", username="testuser1", password="HASHED_PASSWORD"
            )
            u2 = User(
                email="test2@test.com", username="testuser2", password="HASHED_PASSWORD"
            )

            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()

            f = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)

            db.session.add(f)
            db.session.commit()

            # User 2 should be following user 2
            self.assertTrue(User.is_following(u2, u1))
            self.assertFalse(User.is_following(u1, u2))

    def test_user_singup(self):
        """Test user signup method"""

        with app.app_context():
            # Good user
            user = User.signup(
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD",
                image_url="",
            )

            db.session.commit()

            # User with non unique email
            try:
                failed_user1 = User.signup(
                    email="test1@test.com",
                    username="testuser2",
                    password="HASHED_PASSWORD",
                    image_url="",
                )

                return db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()

            # User with no username
            try:
                failed_user2 = User.signup(
                    email="fail2@test.com", password="HASHED_PASSWORD", image_url=""
                )

                return db.session.commit()
            except TypeError:
                db.session.rollback()

            # User with short password
            try:
                failed_user3 = User.signup(
                    email="fail3@test.com",
                    username="testuser4",
                    password="HASH",
                    image_url="",
                )
                return db.session.commit()
            except ValueError:
                db.session.rollback()

            # User should be in database but no others
            self.assertEqual(User.query.filter_by(username="testuser1").first(), user)
            self.assertEqual(User.query.filter_by(username="testuser2").first(), None)
            self.assertEqual(User.query.filter_by(email="fail2@test.com").first(), None)
            self.assertEqual(User.query.filter_by(username="testuser4").first(), None)

    def test_user_authenticate(self):
        """Test user authenticate method"""

        with app.app_context():
            u1 = User.signup(
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD",
                image_url="",
            )

            db.session.commit()

            self.assertEqual(
                User.authenticate(username="testuser1", password="HASHED_PASSWORD"), u1
            )
            self.assertFalse(
                User.authenticate(username="testuser2", password="HASHED_PASSWORD")
            )
            self.assertFalse(
                User.authenticate(username="testuser1", password="HASHED_PASSWOR")
            )
