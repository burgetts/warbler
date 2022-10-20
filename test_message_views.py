"""Message View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()

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

        db.session.commit()

    def test_add_message(self):
        """Test logged in user can add message."""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of our test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_cant_add_message_if_logged_out(self):
        """Ensure you can't add a message if you aren't logged in."""
        resp = self.client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)

        # Make sure there are no messages
        msg = Message.query.all()
        self.assertEqual(len(msg), 0)
        self.assertIn('Access unauthorized.', html)

    def test_delete_message(self):
        """Test that you can delete your own message."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        new_msg = Message(text='post', user_id = sess[CURR_USER_KEY])
        db.session.add(new_msg)
        db.session.commit()

        new_msg = Message.query.filter_by(text='post').first()

        resp = self.client.post(f'/messages/{new_msg.id}/delete')
        self.assertEqual(Message.query.filter_by(text='post').first(), None)
    
    def test_cant_delete_message_if_logged_out(self):
        """Test that you can't delete a message if you're not logged in."""
        new_msg = Message(text='post', user_id = self.testuser.id)
        db.session.add(new_msg)
        db.session.commit()

        resp = self.client.post(f'/messages/{self.testuser.id}/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('Access unauthorized.', html)

        msgs = Message.query.all()
        self.assertEqual(len(msgs), 1)
    
    def test_view_message(self):
        """Test that a logged in user can view a message."""
        new_msg = Message(text='post', user_id = self.testuser.id)
        db.session.add(new_msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        msg = Message.query.filter_by(text='post').first()
        resp = self.client.get(f'/messages/{msg.id}')
        html = resp.get_data(as_text=True)

        self.assertIn(f'<p class="single-message">{msg.text}</p>', html)
    
    def test_cant_view_message_if_logged_out(self):
        new_msg = Message(text='post', user_id = self.testuser.id)
        db.session.add(new_msg)
        db.session.commit()

        msg = Message.query.filter_by(text='post').first()
        resp = self.client.get(f'/messages/{msg.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn('Access unauthorized.', html)
