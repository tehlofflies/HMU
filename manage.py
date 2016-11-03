from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import sqlalchemy

app = Flask(__name__)

engine = sqlalchemy.create_engine('mysql://root:mysql@127.0.0.1') # connect to server
engine.execute("DROP SCHEMA IF EXISTS HMU") 
engine.execute("CREATE SCHEMA HMU") 
engine.execute("USE HMU")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@127.0.0.1/HMU'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class tbl_user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(45))
    user_username = db.Column(db.String(45), unique=True)
    user_password = db.Column(db.String(45))

class tbl_post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    post_user_id = db.Column(db.Integer, nullable=False)
    post_headline = db.Column(db.String(5000))
    post_description = db.Column(db.String(5000))
    post_location = db.Column(db.String(45))
    post_postTime = db.Column(db.DateTime)
    post_meetingTime = db.Column(db.DateTime)

sp_createUser = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_createUser`(
    IN p_name VARCHAR(45),
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(45)
)
BEGIN
    if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into tbl_user
        (
            user_name,
            user_username,
            user_password
        )
        values
        (
            p_name,
            p_username,
            p_password
        );
     
    END IF;
END
"""

sp_validateLogin = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validateLogin`(
IN p_username VARCHAR(45)
)
BEGIN
    select * from tbl_user where user_username = p_username;
END
"""

sp_addPost = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addPost`(
    IN p_headline varchar(45),
    IN p_description varchar(1000),
    IN p_user_id bigint,
    IN p_meetingTime varchar(100),
    IN p_location varchar(1000)
)
BEGIN
    insert into tbl_post(
        post_headline,
        post_description,
        post_user_id,
        post_location,
        post_postTime,
        post_meetingTime
    )
    values
    (
        p_headline,
        p_description,
        p_user_id,
        p_location,
        NOW(),
        p_meetingTime
    );
END
"""

sp_getPosts = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getPosts`()
BEGIN
    select p.post_id, u.user_username, p.post_headline, p.post_description, p.post_location, p.post_postTime, p.post_meetingTime
    from tbl_post as p, tbl_user as u
    where p.post_user_id = u.user_id;
    
END
"""

engine.execute(sp_createUser)
engine.execute(sp_validateLogin)
engine.execute(sp_addPost)
engine.execute(sp_getPosts)


if __name__ == '__main__':
    manager.run()