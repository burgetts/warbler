"""User model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app
app.config['TESTING'] = True 

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # Bulk deletion
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        # Seed 
        u1 = User.signup(username='testuser', email='test@test.com', password='HASHED_PASSWORD', image_url='jpg')
        u2 = User.signup(username='poster', email='post@post.com', password='SECRET', image_url='jpg')
        db.session.commit()

        # u2 posts message
        u2 = User.query.filter_by(username='poster').first()
        new_msg = Message(text='This is a cool message', user_id=u2.id)
        db.session.add(new_msg)
        db.session.commit()

        #u1 likes message
        msg = Message.query.first()
        u1 = User.query.filter_by(username='testuser').first()
        like = Likes(user_id=u1.id, message_id=msg.id)
        db.session.add(like)
        db.session.commit()

        self.client = app.test_client()

    def test_message_model(self):
        """Ensures basic model works."""

        # Check that a message was created and the info is as expected
        all_msg = Message.query.all()
        self.assertEqual(len(all_msg), 1)

        msg = all_msg[0]
        self.assertEqual(msg.user.username, 'poster')

    def test_likes(self):
        """Check that user can like message."""

        like = Likes.query.all()
        self.assertEqual(len(like),1)

        like = like[0]
        user = User.query.filter_by(username='testuser').first()
        self.assertEqual(like.user_id, user.id)
