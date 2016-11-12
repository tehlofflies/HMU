import os
import app as flaskr
import unittest
import tempfile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import sqlalchemy


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
        rv = self.signUp('testName', 'testName.song@columbia.edu', 'password')
        # print(rv.data)
        assert "User created successfully" in rv.data
        #user email has already been created
        rv = self.signUp('testName', 'testName.song@columbia.edu', 'password')
        # print (rv.data)
        assert "Username Exists" in rv.data
        #user email contains illegal characters
        #user email does not contain @
        #username too long
        rv = self.signUp('blahblahblahblahblahblahblahblahblahblahblahblahblahblah', 'blah@columbia.edu', 'password')
        # print (rv.data)
        assert "Data too long" in rv.data
        #password too long
        #email too long

if __name__ == '__main__':
    unittest.main()