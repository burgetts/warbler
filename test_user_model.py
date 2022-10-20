"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app
app.config['TESTING'] = True
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all() #


class UserModelTestCase(TestCase):
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

    def tearDown(self):
        """Rollback session after each test"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.filter_by(username='testuser').first()
    

        # User should have no messages, followers, or likes
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.likes), 0)
    
    def test_repr(self):
        """Test that __repr__ method works as expected."""

        u = User.query.filter_by(username='testuser').first()
        repr = u.__repr__()
        self.assertIn(': testuser, test@test.com>',repr)
    
    def test_is_following(self):
        """Test is is_following method."""
        u2 = User(email='test1@gmail.com', username='testuser2', password='SECRET')
        db.session.add(u2)
        db.session.commit()

        u = User.query.filter_by(username='testuser').first()

        # u following u2
        follow = Follows(user_being_followed_id = u2.id, user_following_id = u.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(u.is_following(u2), True)
        self.assertEqual(u2.is_following(u), False)
    
    def test_is_followed_by(self):
        """Test is_followed_by method."""
        u2 = User(email='test1@gmail.com', username='testuser2', password='SECRET')
        db.session.add(u2)
        db.session.commit()

        u = User.query.filter_by(username='testuser').first()

        # u following u2
        follow = Follows(user_being_followed_id = u2.id, user_following_id = u.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(u.is_followed_by(u2), False)
        self.assertEqual(u2.is_followed_by(u), True)
    
    def test_signup(self):
        """Test signup method."""
        
        valid_user = User.signup(username='validuser', email='valid@valid.com', password='secretpw', image_url='sdgsdg.jpg')
        self.assertIn('valid@valid.com', valid_user.email)

         # Test that user is only created with all 4 inputs
        with self.assertRaises(TypeError):
            User.signup(password='help')

        with self.assertRaises(TypeError):
            User.signup(username='invalid_user', password='help')
        
        with self.assertRaises(TypeError):
            User.signup(username='invalid_user', password='help', email='noemail@gmail.com')
        
       # How to test unique constraint??
        #with self.assertRaises(IntegrityError):
         #   repeat_user = User.signup(username='testuser', email='repeat@test.com', password='secretpw', image_url='sdgsdg.jpg')
          #  db.session.add(repeat_user)
           # db.session.commit()
    
    def test_authentication(self):
        """Test authenticate method."""
        not_user = User.authenticate(username='imadethisup', password='ialsomadethisup')
        self.assertFalse(not_user)

        user = User.authenticate(username="testuser", password="HASHED_PASSWORD")
        self.assertTrue(user)
 
            

            



            
            


    
    
