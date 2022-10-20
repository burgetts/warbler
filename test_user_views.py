"""User view functions tests."""

import os
from unittest import TestCase
from flask import session, g
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY
app.config['TESTING'] = True 
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # Bulk deletion
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        u = User.signup( 
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD", 
            image_url = 'img.jpg')

        db.session.commit()
        self.client = app.test_client()
        self.change_session = self.client.session_transaction() 
    
    def setup_followers(self):
        """Set up followers for testing."""
        user2 = User.signup(email="user2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD", 
            image_url = 'img.jpg')
        db.session.commit()

        follower = User.query.filter_by(username='testuser').first()
        followee = User.query.filter_by(username='testuser2').first()

        # testuser follows testuser2
        new_follow = Follows(user_being_followed_id=followee.id, user_following_id=follower.id)
        db.session.add(new_follow)
        db.session.commit()

    def test_signup(self):
        """Test signup route."""
        # Check correct form displayed
        resp = self.client.get('/signup')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Sign me up!</button>', html)
        
        # Check user signup leads to their homepage
        resp = self.client.post('/signup', data={'username': 'test', 'email':'test@testing.com', 'password':'password', 'image_url': 'img.jpg'}, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<p>@test</p>', html)
    
    def test_login(self):
        """Test login route."""
        # Check correct form displayed
        resp = self.client.get('/login')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Welcome back', html)
       
       # Test login works for valid user
        resp = self.client.post('/login', data={'username': 'testuser','password':'HASHED_PASSWORD'}, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello, testuser!', html)

       # Test login doesn't work for invalid user
        resp = self.client.post('/login', data={'username': 'doesnotexist','password':'password'})
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Welcome back', html)
    
    def test_logout(self):
        """Test logout route."""
        # TO DO: Ensure there is no user id in session
        resp = self.client.get('/logout', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-message">You&#39;ve been logged out.</div>', html)

    
    def test_display_followers(self):
        """Test followers and following pages."""
        self.setup_followers()
        follower = User.query.filter_by(username='testuser').first()
        followee = User.query.filter_by(username='testuser2').first()

        with self.client.session_transaction() as change_session:
            change_session['curr_user'] = follower.id

        # Test following
        resp = self.client.get(f'/users/{follower.id}/following', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<p class="card-bio">{followee.bio}</p>', html)

        # Test followers
        resp = self.client.get(f'/users/{followee.id}/followers', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<p class="card-bio">{follower.bio}</p>', html)
    
    def show_all_likes(self):
        """Test display of all user's likes."""

        # u2 posts message
        self.setup_followers()
        u2 = User.query.filter_by(username='testuser2').first()
        new_msg = Message(text='This is a cool message', user_id=u2.id)
        db.session.add(new_msg)
        db.session.commit()

        #u1 likes message
        msg = Message.query.first()
        u1 = User.query.filter_by(username='testuser').first()
        like = Likes(user_id=u1.id, message_id=msg.id)
        db.session.add(like)
        db.session.commit()

        # Test that u2's message is in u1's likes
        resp = self.client.get(f'/users/{u1.id}/likes')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<p>{msg.text}</p>', html)
  
    def test_cant_delete_user_if_logged_out(self):
        """Test user can't delete another user if they are logged out."""
        resp = self.client.post('/users/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_cant_see_followers_if_logged_out(self):
        """Test user can't see follwers page if they are logged out."""
        resp = self.client.get(f'/users/1/followers', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    # How to test routes that user g.user as authentication?









    


            

            



            
            


    
    
