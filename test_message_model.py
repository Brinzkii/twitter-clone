"""User model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

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


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, clear existing sample data."""

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()

            db.session.commit()

            self.client = app.test_client()

    def test_message_model(self):
        """Test basic model"""

        with app.app_context():
            u = User.signup(
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD",
                image_url="",
            )

            db.session.commit()

            msg = Message(user_id=u.id, text="test")

            db.session.add(msg)
            db.session.commit()

            self.assertEqual(Message.query.first(), msg)
            self.assertEqual(msg.user_id, u.id)
            self.assertEqual(msg.user, u)
            self.assertEqual(Message.query.filter_by(text="test").first(), msg)
