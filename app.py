from __future__ import print_function # In python 2.7
import sys
import datetime

from flask import Flask, render_template, json, request, redirect, session, flash
from flaskext.mysql import MySQL

from flask_wtf import Form
from wtforms import DateField

mysql = MySQL()
app = Flask(__name__)

app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mysql'
app.config['MYSQL_DATABASE_DB'] = 'HMU'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

class DateForm(Form):
    dt = DateField('Pick a Date', format="%m/%d/%Y")

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password and not _name.isspace() and not _password.isspace():

            if "@" not in _email:
                flash("Invalid email", category='error')
                return redirect('/showSignUp')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_createUser', (_name, _email, _password))
            data = cursor.fetchall()

            if len(data) is 0:
                # user signed up successfully
                conn.commit()

                # sign the user in/get user session
                cursor.callproc('sp_validateLogin', (_email,))
                data1 = cursor.fetchall()
                session['user'] = data1[0][0]

                # create a user profile
                cursor.callproc('sp_createProfile', (_name, "", _email, None, None))
                data2 = cursor.fetchall()

                if len(data2) is 0:
                    conn.commit()
                    return redirect('/showEditProfile') 
                else:
                    return render_template('error.html', error='An error occurred!')

            else:
                flash(str(data[0]), category='error')
                return redirect('/showSignUp')

            cursor.close()
            conn.close()
        else:
            flash("Enter all the required fields", category='error')
            return redirect('/showSignUp')
            
    except Exception as e:
        flash(str(e), category='error')
        return redirect('/showSignUp')

@app.route('/showSignIn')
def showSignIn():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
       
        if _username and _password and not _password.isspace():
            # connect to mysql
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_validateLogin', (_username,))
            data = cursor.fetchall()

            if len(data) > 0:
                if str(data[0][3])==_password:
                    session['user'] = data[0][0]
                    return redirect('/userHome')
                else:
                    flash("Password is not correct", category='error')
                    return redirect('/showSignIn')
            else:
                flash("Email address does not exist", category='error')
                return redirect('/showSignIn')
            cursor.close()
            con.close()

        else:
            flash("Enter the required fields", category='error')
            return redirect('/showSignIn')

    except Exception as e:
        return render_template('error.html', error=str(e))
        
@app.route('/showAddPost')
def showAddPost():
    form = DateForm()
    return render_template('addPost.html', form=form)

@app.route('/addPost', methods=['POST'])
def addPost():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _headline = request.form['inputHeadline']
            _location = request.form['inputLocation']

            if 'inputDescription' in request.form:
                _description = request.form['inputDescription']
            else:
                _description = ""

            if 'inputMeetingDate' in request.form:
                _unformattedDate = request.form['inputMeetingDate']
            else: 
                form = DateForm(request.form)
                _unformattedDate = form.dt.data.strftime('%x')
            
            _user = session.get('user')
            _unformattedTime = request.form['inputMeetingTime']
                        
            if _headline and not _headline.isspace() and _location \
            and not _location.isspace() and _unformattedTime is not None \
            and _unformattedDate is not None:
                _formattedDate = datetime.datetime.strptime(_unformattedDate, '%m/%d/%y')
                formattedTime = datetime.datetime.strptime(_unformattedTime, '%H:%M').time()
                _formattedDatetime = datetime.datetime.combine(_formattedDate, formattedTime)

                if(_formattedDatetime < datetime.datetime.today()): 
                    flash("Date/Time must be in future", category='error')
                    return redirect('/showAddPost')
                
                cursor.callproc('sp_addPost', (_headline, _description, _user, _formattedDatetime, _location))
                data = cursor.fetchall()

                if len(data) is 0:
                    conn.commit()
                    return redirect('/userHome')
                else:
                    flash("An error occurred!", category='error')
                    return redirect('/showAddPost')

            else:
                flash("Enter all the required fields", category='error')
                return redirect('/showAddPost')
        else:
            flash("Unauthorized Access", category='error')
            return redirect('/showAddPost')
    except Exception as e:
        flash(str(e), category='error')
        return redirect('/showAddPost')
    finally:
        cursor.close()
        conn.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error='Unauthorized Access')

@app.route('/getPost')
def getPost():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):

            # is the user following the authors of the posts?
            _user = session.get('user')
            cursor.callproc('sp_getFollowing', (_user,))
            followings = cursor.fetchall()

            followings_dict = {}
            for following in followings:
                followings_dict[following[0]] = True

            # get posts
            cursor.callproc('sp_getPosts')
            posts = cursor.fetchall()

            posts_dict = []
            for post in posts:

                # set a display or no display option if the post author is being followed
                # this dict entry gets used for css styling, see showPosts.js
                display_option = "filter"
                if post[2] in followings_dict:
                    display_option = "no-filter"
                if post[2] == _user:
                    display_option = "no-filter"

                post_dict = {
                    'Id': post[0],
                    'User': post[1],
                    'UserId': post[2],
                    'Headline': post[3],
                    'Description': post[4],
                    'Location': post[5],
                    'PostTime': post[6].strftime("%B %d, %Y, %I:%M %p"),
                    'MeetingTime': post[7].strftime("%B %d, %Y, %I:%M %p"),
                    'Filter': display_option
                }
                posts_dict.append(post_dict)

            return json.dumps(posts_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/deletePost/<post_id>')
def deletePost(post_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            cursor.callproc('sp_getPostInfo', (post_id,))
            results = cursor.fetchall()
            post_user = results[0][1]
            if post_user == session.get('user'):
                cursor.callproc('sp_deletePost', (post_id,))
                conn.commit()
                return redirect('/userHome')
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()        

@app.route('/showEditProfile')
def showEditProfile():
    if session.get('user'):
        _id = session.get('user')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getProfile', (str(_id),))
        data = cursor.fetchall()

        _name = data[0][1]
        _email = data[0][3]

        if data[0][2] is None or len(data[0][2]) == 0:
            _description = ""
        else:
            _description = data[0][2]
        if data[0][4] is None or len(data[0][4]) == 0:
            _phone = ""
        else:
            _phone = data[0][4]
        if data[0][5] is None or len(data[0][5]) == 0:
            _facebook = ""
        else:
            _facebook = data[0][5]

        return render_template('editprofile.html', 
            name=_name, 
            description=_description, 
            email=_email, 
            phone=_phone, 
            facebook=_facebook
        )

        cursor.close()
        conn.close()
    else:
        return render_template('error.html', error='Unauthorized Access')

@app.route('/editProfile', methods=['POST'])
def editProfile():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _name = request.form['inputName']
            _description = request.form['inputDescription']
            _email = request.form['inputEmail']
            """
            if not request.form['inputPhone']:
                _phone = ""
            else:
                _phone = request.form['inputPhone']
            if not request.form['inputFacebook']:
                _facebook = ""
            else:
                _facebook = request.form['inputFacebook']
            """
            _phone = request.form['inputPhone']
            _facebook = request.form['inputFacebook']
            _id = session.get('user')
            cursor.callproc('sp_editProfile', (_name, _description, _email, _phone, _facebook))
            conn.commit()
            return redirect('/me')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        conn.close()
        cursor.close()

@app.route('/me')
def userMe():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _user = session.get('user')
            cursor.callproc('sp_getProfile', (str(_user),))
            infos = cursor.fetchall()

            for info in infos:
                name = info[1]
                bio = info[2]
                email = info[3]
                phone = info[4]
                fb = info[5]

            return render_template('userProfile.html', 
                me = 1,
                user_id = _user, 
                name = name,
                bio = bio,
                email = email,
                phone = phone,
                fb = fb
            )
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/user/<user_id>')
def user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            if int(user_id) == session.get('user'):
                return redirect('/me')

            cursor.callproc('sp_getProfile', (user_id,))
            infos = cursor.fetchall()

            for info in infos:
                name = info[1]
                bio = info[2]
                email = info[3]
                phone = info[4]
                fb = info[5]

            cursor.callproc('sp_getFollowingIds', (str(session.get('user')),))
            results = cursor.fetchall()
            following = 0
            for result in results:
                if result[2] == int(user_id):
                    following = 1

            return render_template('userProfile.html', 
                me = 0,
                following = following,
                user_id = user_id, 
                name = name,
                bio = bio,
                email = email,
                phone = phone,
                fb = fb
            )

        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/follow/<followed_user_id>')
def addFollow(followed_user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _follower_user_id = session.get('user')
            _followed_user_id = int(followed_user_id)

            #check that this row does not already exist in the table
            cursor.callproc('sp_checkFollow', (_follower_user_id, _followed_user_id))
            results = cursor.fetchall()
            if len(results) == 0:
                cursor.callproc('sp_addFollow', (_follower_user_id, _followed_user_id))
                conn.commit()
                
                cursor.callproc('sp_getProfile', (_followed_user_id,))
                infos = cursor.fetchall()

                for info in infos:
                    name = info[1]
                    bio = info[2]
                    email = info[3]
                    phone = info[4]
                    fb = info[5]

                return render_template('userProfile.html', 
                    me = 0,
                    user_id = _followed_user_id, 
                    name = name,
                    bio = bio,
                    email = email,
                    phone = phone,
                    fb = fb,
                    following = 1
                )
            else:
                return render_template('error.html', error='Already following')
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/unfollow/<followed_user_id>')
def deleteFollow(followed_user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _follower_user_id = session.get('user')
            _followed_user_id = int(followed_user_id)
            cursor.callproc('sp_deleteFollow', (_follower_user_id, _followed_user_id))
            conn.commit()
            
            cursor.callproc('sp_getProfile', (_followed_user_id,))
            infos = cursor.fetchall()

            for info in infos:
                name = info[1]
                bio = info[2]
                email = info[3]
                phone = info[4]
                fb = info[5]

            return render_template('userProfile.html', 
                me = 0,
                user_id = _followed_user_id, 
                name = name,
                bio = bio,
                email = email,
                phone = phone,
                fb = fb,
                following = 0
            )
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/following')
def showFollowing():
    if session.get('user'):
        return render_template('following.html')
    else:
        return render_template('error.html', error='Unauthorized Access')
 
@app.route('/getFollowing')
def getFollowing():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _user = session.get('user')
            cursor.callproc('sp_getFollowing', (_user,))
            followings = cursor.fetchall()

            followings_dict = []
            for following in followings:
                following_dict = {
                    'FollowedId': following[0],
                    'FollowedName': following[1]
                }
                followings_dict.append(following_dict)

            return json.dumps(followings_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/users')
def showUsers():
    if session.get('user'):
        return render_template('users.html')
    else:
        return render_template('error.html', error='Unauthorized Access')

@app.route('/getUsers')
def getUsers():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            cursor.callproc('sp_getUsers')
            users = cursor.fetchall()

            users_dict = []
            for user in users:
                user_dict = {
                    'Id': user[0],
                    'Name': user[1],
                    'Bio': user[2],
                    'Email': user[3],
                    'Phone': user[4],
                    'Fb': user[5]
                }
                users_dict.append(user_dict)

            return json.dumps(users_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)