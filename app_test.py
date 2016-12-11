import os
import app as flaskr
import unittest
import tempfile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import sqlalchemy

import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        # with flaskr.app.app_context():
        #     flaskr.init_db()

        self.app.engine = sqlalchemy.create_engine('mysql://root:@127.0.0.1')
        #self.app.engine.execute("DROP SCHEMA IF EXISTS HMU_TEST") 
        #self.app.engine.execute("CREATE SCHEMA HMU_TEST") 
        self.app.engine.execute("USE HMU_TEST")

        flaskr.app.config['MYSQL_DATABASE_DB'] = 'HMU_TEST'
        flaskr.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/HMU_TEST'


    def tearDown(self):
        self.app.engine = sqlalchemy.create_engine('mysql://root:@127.0.0.1')
        self.app.engine.execute("USE HMU_TEST")
        self.app.engine.execute("TRUNCATE TABLE TBL_USER")
        self.app.engine.execute("TRUNCATE TABLE TBL_POST")
        self.app.engine.execute("TRUNCATE TABLE TBL_PROFILE")

        
    def signUp(self, name, email, password):
        return self.app.post('/signUp', data=dict(
            inputName=name, 
            inputEmail=email, 
            inputPassword=password
            ), follow_redirects=True)


    def test_signUp(self):
        #user email has not been created
        rv = self.signUp('testName', 'testName@columbia.edu', 'password')
        assert "Edit Your Profile!" in rv.data
        #user email has already been created
        rv = self.signUp('testName', 'testName@columbia.edu', 'password')
        assert "Username Exists" in rv.data
        #user email does not contain @
        rv = self.signUp('newTestName', 'newTestNamecolumbia.edu', 'password')
        assert "Invalid email" in rv.data
        #username too long
        rv = self.signUp('Blahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'blah@columbia.edu', 'blah')
        assert "Data too long" in rv.data
        #email too long
        rv = self.signUp('blah', 'blahhhhhhhhhhhhhhhhhhhhhhhhhhhhhh@columbia.edu', 'blah')
        assert "Data too long" in rv.data
        #password too long
        rv = self.signUp('blah', 'blah@columbia.edu', 'blahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
        assert "Data too long" in rv.data
        #missing name
        rv = self.signUp('', 'testName@columbia.edu', 'password')
        assert "Enter all the required fields" in rv.data
        #missing email
        rv = self.signUp('testName', '', 'password')
        assert "Enter all the required fields" in rv.data
        #missing password
        rv = self.signUp('testName', 'testName@columbia.edu', '')
        assert "Enter all the required fields" in rv.data


    def editProfile(self, name, bio, email, phone, facebook):
        return self.app.post('/editProfile', data=dict(
            inputName=name,
            inputDescription=bio,
            inputEmail=email,
            inputPhone=phone,
            inputFacebook=facebook
            ), follow_redirects=True)


    def test_editProfile(self):
        self.signUp('testName', 'testName@columbia.edu', 'password')
        # keep name and email the same and add required field bio
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '', '')
        assert "My Profile" in rv.data
        # enter a bad name
        rv = self.editProfile('   ', 'bio', 'testName@columbia.edu', '', '')
        assert "Please give valid entries for required fields" in rv.data
        # remove name
        rv = self.editProfile('', 'bio', 'testName@columbia.edu', '', '')
        assert "Please give valid entries for required fields" in rv.data
        # enter a bad bio
        rv = self.editProfile('testName', '   ', 'testName@columbia.edu', '', '')
        assert "Please give valid entries for required fields" in rv.data
        # remove bio
        rv = self.editProfile('testName', '', 'testName@columbia.edu', '', '')
        assert "Please give valid entries for required fields" in rv.data
        # somehow try to change your email
        rv = self.editProfile('testName', 'bio', 'new@columbia.edu', '', '')
        assert "testName@columbia.edu" in rv.data
        # remove email
        rv = self.editProfile('testName', 'bio', '', '', '')
        assert "Please give valid entries for required fields" in rv.data
        # enter a phone number that isn't 10 digits
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '123', '')
        assert "Not a valid phone number" in rv.data
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '00123456789', '')
        assert "Not a valid phone number" in rv.data
        # enter a phone number with characters other than numbers
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '0a23!5d7e9', '')
        assert "Not a valid phone number" in rv.data
        # enter a proper phone number
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '0123456789', '')
        assert "My Profile" in rv.data
        # enter a proper phone number with optional facebook
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '0123456789', 'https:facebook.com')
        assert "My Profile" in rv.data
        # enter a bad facebook url
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '', '   ')
        assert "Not a valid Facebook URL" in rv.data
        # successful edit profile
        rv = self.editProfile('testName', 'bio', 'testName@columbia.edu', '0123456789', 'http://facebook.com')
        assert "Edit Profile" in rv.data

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_logout(self):
        rv = self.signUp('testName', 'testName@columbia.edu', 'password')
        assert "Edit Your Profile!" in rv.data
        # user is successfully logged in
        self.logout()
        rv = self.app.get('/userHome')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/following')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/getFollowing')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/follow/1')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/unfollow/1')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/deletePost/1')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/getPost')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/showAddPost')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/user/1')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/me')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/getFollowing')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/showEditProfile')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/getUsers')
        assert "Unauthorized Access" in rv.data
        rv = self.app.get('/users')
        assert "Unauthorized Access" in rv.data
        # user is logged out and unable to view newsfeed


    def signIn(self, email, password):
        return self.app.post('/validateLogin', data=dict(
            inputEmail=email,
            inputPassword=password
            ), follow_redirects=True)


    def test_signIn(self):
        #missing email
        rv = self.signIn('', 'password')
        assert "Enter the required fields" in rv.data
        #missing password
        rv = self.signIn('testName@columbia.edu', '')
        assert "Enter the required fields" in rv.data
        #user email does not exist
        rv = self.signIn('testName@columbia.edu', 'password')
        assert "Email address does not exist" in rv.data
        #user password is a space
        rv = self.signIn('testName@columbia.edu', ' ')
        assert "Enter the required fields" in rv.data
        #user email exists but password incorrect
        self.signUp('testName', 'testName@columbia.edu', 'password')
        self.logout()
        rv = self.signIn('testName@columbia.edu', 'wrongpassword')
        assert "Password is not correct" in rv.data
        #user email exists and password correct
        rv = self.signIn('testName@columbia.edu', 'password')
        assert "Welcome to HMU!" in rv.data


    def addPost(self, headline, description, unformattedTime, unformattedDate, location):
        return self.app.post('/addPost', data=dict(
            inputHeadline=headline,
            inputDescription=description,
            inputMeetingTime=unformattedTime,
            inputMeetingDate=unformattedDate,
            inputLocation=location
            ), follow_redirects=True)


    def test_addPost(self):
        self.signUp('testName', 'testName@columbia.edu', 'password')
        d = datetime.datetime.today() + datetime.timedelta(days=1)
        tomorrow = d.strftime("%m/%d/%y")
        d = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday = d.strftime("%m/%d/%y")
        #successful post with all required fields w/ description
        rv = self.addPost('Lunch', 'Hang out with me pls', '12:00', tomorrow, 'Ferris')
        assert "Welcome to HMU!" in rv.data
        #successful post with all required fields w/o description
        rv = self.addPost('Lunch', None, '12:00', tomorrow, 'Ferris')
        assert "Welcome to HMU!" in rv.data
        #missing field - time
        rv = self.addPost('Lunch', 'Hang out with me pls', None, tomorrow, 'Ferris')
        assert "400: Bad Request" in rv.data
        #missing field - location
        rv = self.addPost('Lunch', 'Hang out with me pls', '12:00', tomorrow, None)
        assert "400: Bad Request" in rv.data
        #missing field - headline
        rv = self.addPost(None, 'Hang out with me pls', '12:00', tomorrow, 'Ferris')
        assert "400: Bad Request" in rv.data
        #invalid field - meetup date and time entered is before current date and time
        rv = self.addPost('Lunch', 'Hang out with me pls', '12:00', yesterday, None)
        assert "400: Bad Request" in rv.data
        # assert "Date/Time must be in future" in rv.data
        #invalid field - headline too long (over character limit of 45)
        rv = self.addPost('Blahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'Hang out with me pls', '12:00', tomorrow, 'Ferris')
        assert "Data too long" in rv.data
        #invalid field - location too long (over character limit of 1000)
        location = "hello" * 201
        rv = self.addPost('Lunch', 'Hang out with me pls', '12:00', tomorrow, location)
        assert "Data too long" in rv.data
        #invalid field - description too long (over character limit of 1000)
        description = "hello" * 201        
        rv = self.addPost('Lunch', description, '12:00', tomorrow, 'Ferris')
        assert "Data too long" in rv.data

    def deletePost(self, post_id):
        return self.app.get('/deletePost/'+ str(post_id), follow_redirects=True)

    def test_deletePost(self):
        self.signUp('testName', 'testName@columbia.edu', 'password')
        d = datetime.datetime.today() + datetime.timedelta(days=1)
        tomorrow = d.strftime("%m/%d/%y")
        rv = self.addPost('Lunch', 'Hang out with me pls', '12:00', tomorrow, 'Ferris')
        assert "Welcome to HMU!" in rv.data
        #successful post with all required fields w/ description
        rv = self.deletePost(1)
        assert "Welcome to HMU!" in rv.data
        # successful post deletion, return to newsfeed
        rv = self.deletePost(1)
        assert "tuple index out of range" in rv.data
        # post has already been deleted

    def test_directory(self):
        self.signUp('testName', 'testName@columbia.edu', 'password')
        rv = self.app.get('/users')
        assert "new testName" not in rv.data
        # directory contains only users that have been created
        self.signUp('new testName', 'newTestName@columbia.edu', 'password')
        rv = self.app.get('/getUsers')
        assert "new testName" in rv.data
        # directory contains new user that was created


### Newsfeed/Posts tests
    def getPost(self):
        return self.app.get('/getPost', follow_redirects=True)

    def test_getPost(self):
        self.signUp('testName', 'testName@columbia.edu', 'password')
        d = datetime.datetime.today() + datetime.timedelta(days=1)
        tomorrow = d.strftime("%m/%d/%y")
        #successful post with all required fields w/ description
        self.addPost('Lunch', 'Hang out with me pls', '12:00', tomorrow, 'Ferris')
        rv = self.getPost()
        assert "Ferris" in rv.data


### User Profile tests
    def getUser(self, user_id):
        return self.app.get('/user/'+user_id, follow_redirects=True)

    def getMe(self):
        return self.app.get('/me', follow_redirects=True)

    def test_getProfile(self):
        self.signUp('User1', 'user1@columbia.edu', 'password')
        self.editProfile('User1', 'bio', 'user1@columbia.edu', '', '')
        self.logout
        self.signUp('User2', 'user2@columbia.edu', 'password')
        self.editProfile('User2', 'bio', 'user2@columbia.edu', '', '')
        # Get another user's profile page
        rv = self.getUser('1')
        assert "Meet User1" in rv.data
        # Redirect to get my own profile page
        rv = self.getUser('2')
        assert "Edit Profile" in rv.data
        # Get my profile page through /me
        rv = self.getMe()
        assert "Edit Profile" in rv.data


### Follow tests
    def addFollow(self, user_id):
        return self.app.get('/follow/'+user_id, follow_redirects=True)

    def deleteFollow(self, user_id):
        return self.app.get('/unfollow/'+user_id, follow_redirects=True)

    def getFollowing(self):
        rv = self.app.get('/following', follow_redirects=True)
        assert "Who I'm Following" in rv.data
        assert "User1" not in rv.data
        return self.app.get('/getFollowing', follow_redirects=True)

    def test_following(self):
        self.signUp('User1', 'user1@columbia.edu', 'password')
        self.editProfile('User1', 'bio', 'user1@columbia.edu', '', '')
        self.logout()
        self.signUp('User2', 'user2@columbia.edu', 'password')
        self.editProfile('User2', 'bio', 'user2@columbia.edu', '', '')
        # Follow user 1
        rv = self.addFollow('1')
        # User 1's profile page should now show option to unfollow
        assert "Unfollow Me" in rv.data
        # Check user 1 is in following list
        rv = self.getFollowing()
        assert "User1" in rv.data
        # Try to follow user 1 again
        rv = self.addFollow('1')
        assert "Already following" in rv.data
        # Unfollow user 1
        rv = self.deleteFollow('1')
        # User 1's profile page should now show option to follow again
        assert "Follow Me" in rv.data
        # Check user 1 is not following list anymore
        rv = self.getFollowing()
        assert "User1" not in rv.data
        self.logout()        


if __name__ == '__main__':
    unittest.main()
