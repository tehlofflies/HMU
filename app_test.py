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

        self.app.engine = sqlalchemy.create_engine('mysql://root:mysql@127.0.0.1')
        # self.app.engine.execute("DROP SCHEMA IF EXISTS HMU_TEST") 
        # self.app.engine.execute("CREATE SCHEMA HMU_TEST") 
        self.app.engine.execute("USE HMU_TEST")

        flaskr.app.config['MYSQL_DATABASE_DB'] = 'HMU_TEST'
        flaskr.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@127.0.0.1/HMU_TEST'

    def tearDown(self):
        self.app.engine.execute("TRUNCATE TABLE TBL_USER")
        self.app.engine.execute("TRUNCATE TABLE TBL_POST")

        
    def signUp(self, name, email, password):
        return self.app.post('/signUp', data=dict(
            inputName=name, 
            inputEmail=email, 
            inputPassword=password
            ), follow_redirects=True)

    def test_signUp(self):
        #user email has not been created
        rv = self.signUp('testName', 'testName@columbia.edu', 'password')
        assert "User created successfully" in rv.data
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

    def signIn(self, email, password):
        return self.app.post('/validateLogin', data=dict(
            inputEmail=email,
            inputPassword=password
            ), follow_redirects=True)

    def test_signIn(self):
        #user email does not exist
        rv = self.signIn('testName@columbia.edu', 'password')
        assert "Email address does not exist" in rv.data
        #user email exists and password correct
        self.signUp('testName', 'testName@columbia.edu', 'password')
        rv = self.signIn('testName@columbia.edu', 'password')
        assert "Welcome to HMU!" in rv.data
        #user email exists but password incorrect
        rv = self.signIn('testName@columbia.edu', 'wrongpassword')
        assert "Password is not correct" in rv.data

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
        self.signIn('testName@columbia.edu', 'password')
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
        assert "Date/Time must be in future" in rv.data
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

if __name__ == '__main__':
    unittest.main()