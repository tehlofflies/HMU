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

class tbl_profile(db.Model):
    profile_id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(45))
    profile_bio = db.Column(db.String(5000))
    profile_username = db.Column(db.String(45), unique=True)
    profile_phone = db.Column(db.String(10))
    profile_facebook = db.Column(db.String(45)) 

class tbl_follow(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    follower_user_id = db.Column(db.Integer, nullable=False)
    followed_user_id = db.Column(db.Integer, nullable=False)

class tbl_interested(db.Model):
    interested_id = db.Column(db.Integer, primary_key=True)
    interested_user_id = db.Column(db.Integer, nullable=False)
    interested_post_id = db.Column(db.Integer, nullable=False)

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
    select *
    from (
        select p.post_id, u.user_name, u.user_id, p.post_headline, p.post_description, p.post_location, p.post_postTime, p.post_meetingTime
        from tbl_post as p, tbl_user as u
        where p.post_user_id = u.user_id) x join (
        select interested_post_id, count(interested_user_id)
        from tbl_interested group by interested_post_id) i on x.post_id = i.interested_post_id
    where post_meetingTime > NOW()
    order by post_meetingTime asc
    ;
    
END
"""


sp_getPostUserId = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getPostUserId`(
    IN p_id bigint
)
BEGIN
    select post_user_id from tbl_post
    where post_id = p_id 
    ;   
END
"""

sp_deletePost = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deletePost`(
    IN p_id bigint
)
BEGIN
    delete from tbl_post
    where post_id = p_id
    ;
END
"""

sp_createProfile = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_createProfile`(
    IN p_name VARCHAR(45),
    IN p_bio VARCHAR(5000),
    IN p_username VARCHAR(45),
    IN p_phone VARCHAR(10),
    IN p_facebook VARCHAR(45)
)
BEGIN
 	insert into tbl_profile
    (
        profile_name,
        profile_bio,
        profile_username,
        profile_phone,
        profile_facebook
    )
    values
    (
        p_name,
        p_bio,
        p_username,
        p_phone,
        p_facebook
    );
END
"""

sp_editProfile = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_editProfile`(
    IN p_name VARCHAR(45),
    IN p_bio VARCHAR(5000),
    IN p_username VARCHAR(45),
    IN p_phone VARCHAR(10),
    IN p_facebook VARCHAR(45)
)
BEGIN
    UPDATE tbl_profile SET 
        profile_name = p_name,
        profile_bio = p_bio,
        profile_phone = p_phone,
        profile_facebook = p_facebook
    WHERE 
        profile_username = p_username
    ;
END
"""

sp_deleteUser = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUser`(
    IN p_user_id bigint
)
BEGIN
    delete from tbl_user
    where user_id = p_user_id;
END
"""

sp_deleteUserPost = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUserPost`(
    IN p_user_id bigint
)
BEGIN
    delete from tbl_post
    where post_user_id = p_user_id;
END
"""

sp_deleteUserProfile = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUserProfile`(
    IN p_user_id bigint
)
BEGIN
    delete from tbl_profile
    where profile_id = p_user_id;
END
"""

sp_deleteUserInterested = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUserInterested`(
    IN p_user_id bigint
)
BEGIN
    delete from tbl_interested
    where interested_user_id = p_user_id;
END
"""

sp_deleteUserFollow = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_deleteUserFollow`(
    IN p_user_id bigint
)
BEGIN
    delete from tbl_follow
    where follower_user_id = p_user_id or followed_user_id = p_user_id;
END
"""

sp_getProfile = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getProfile`(
    IN p_user_id bigint
)
BEGIN
    select * from tbl_profile where profile_id = p_user_id;    
END
"""

sp_checkFollow = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_checkFollow`(
    IN p_follower_user_id bigint,
    IN p_followed_user_id bigint
)
BEGIN
    select * from tbl_follow
    where follower_user_id = p_follower_user_id
    and followed_user_id = p_followed_user_id
    ;
END
"""

sp_addFollow = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_addFollow`(
    IN p_follower_user_id bigint,
    IN p_followed_user_id bigint
)
BEGIN
    insert into tbl_follow
    (
        follower_user_id,
        followed_user_id
    )
    values
    (
        p_follower_user_id,
        p_followed_user_id
    );
END
"""

sp_deleteFollow = """
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_deleteFollow`(
    IN p_follower_user_id bigint,
    IN p_followed_user_id bigint
)
BEGIN
    delete from tbl_follow
    where follower_user_id=p_follower_user_id
    and followed_user_id=p_followed_user_id
    ;
END
"""

sp_getFollowing = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getFollowing`(
    IN p_user_id bigint
)
BEGIN
    select f.followed_user_id, u.user_name
    from tbl_follow as f, tbl_user as u
    where f.follower_user_id = p_user_id and f.followed_user_id = u.user_id;
    
END
"""

sp_getFollowers = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getFollowers`(
    IN p_user_id bigint
)
BEGIN
    select f.follower_user_id, u.user_name
    from tbl_follow as f, tbl_user as u
    where f.followed_user_id = p_user_id and f.follower_user_id = u.user_id;
    
END
"""

sp_getFollowingIds = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getFollowingIds`(
    IN p_user_id bigint
)
BEGIN
    select *
    from tbl_follow
    where follower_user_id = p_user_id
    ;
END
"""

sp_getUsers = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getUsers`()
BEGIN
    select * from tbl_profile
    order by profile_name asc;
    
END
"""

sp_addInterest = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addInterest`(
    IN p_user_id bigint,
    IN p_post_id bigint
)
BEGIN
    insert into tbl_interested(
        interested_user_id,
        interested_post_id
    )
    values
    (
        p_user_id,
        p_post_id
    );
END
"""

sp_removeInterest = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_removeInterest`(
    IN p_user_id bigint,
    IN p_post_id bigint
)
BEGIN
    delete from tbl_interested
    where interested_user_id=p_user_id
    and interested_post_id=p_post_id
    ;
END
"""

sp_getPostInterest= """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getPostInterest`(
    IN p_user_id bigint,
    IN p_post_id bigint
)
BEGIN
    select * from tbl_interested
    where interested_user_id = p_user_id
    and interested_post_id = p_post_id
    ;
END
"""

sp_getPostInfo = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getPostInfo`(
    IN p_post_id bigint
)
BEGIN
    select u.user_name, p.post_headline, p.post_description, p.post_postTime, p.post_meetingTime, p.post_location, u.user_id, u.user_username
    from tbl_post as p, tbl_user as u
    where p.post_user_id = u.user_id AND p_post_id = p.post_id
    ;
END
"""

sp_getInterestedUsers = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getInterestedUsers`(
    IN p_post_id bigint
)
BEGIN
    select u.user_id, u.user_name
    from tbl_post as p, tbl_user as u, tbl_interested as i
    where p.post_id = p_post_id and p.post_id = i.interested_post_id and u.user_id = i.interested_user_id
    ;
END
"""

sp_getNewestPostId = """
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getNewestPostId`()
BEGIN
    select MAX(post_id)
    from tbl_post
    ;
END
"""

engine.execute(sp_createUser)
engine.execute(sp_validateLogin)
engine.execute(sp_addPost)
engine.execute(sp_getPosts)
engine.execute(sp_getPostUserId)
engine.execute(sp_deletePost)
engine.execute(sp_checkFollow)
engine.execute(sp_addFollow)
engine.execute(sp_deleteFollow)
engine.execute("set global sql_mode = 'strict_trans_tables';")
engine.execute(sp_createProfile)
engine.execute(sp_editProfile)
engine.execute(sp_deleteUser)
engine.execute(sp_deleteUserPost)
engine.execute(sp_deleteUserProfile)
engine.execute(sp_deleteUserFollow)
engine.execute(sp_deleteUserInterested)
engine.execute(sp_getProfile)
engine.execute(sp_getFollowing)
engine.execute(sp_getFollowers)
engine.execute(sp_getFollowingIds)
engine.execute(sp_getUsers)
engine.execute(sp_addInterest)
engine.execute(sp_removeInterest)
engine.execute(sp_getPostInterest)
engine.execute(sp_getPostInfo)
engine.execute(sp_getInterestedUsers)
engine.execute(sp_getNewestPostId)

if __name__ == '__main__':
    manager.run()
