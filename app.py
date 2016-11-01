from __future__ import print_function # In python 2.7
import sys

from flask import Flask, render_template, json, request, redirect, session, jsonify
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash


mysql = MySQL()
app = Flask(__name__)

app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mysql'
app.config['MYSQL_DATABASE_DB'] = 'HMUFriends'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignIn')
def showSignIn():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_createUser',(_name,_email,_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully!'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
       
        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][3])==_password:
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/showAddPost')
def showAddPost():
    return render_template('addPost.html')

@app.route('/addPost',methods=['POST'])
def addPost():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            print('goodbye',file=sys.stderr)
            _headline = request.form['inputHeadline']
            print('jason',file=sys.stderr)
            _description = request.form['inputDescription']
            print('monica',file=sys.stderr)
            _user = session.get('user')
            _meetingTime = request.form['inputMeetingTime']
            _location = request.form['inputLocation']

            cursor.callproc('sp_addPost',(_headline, _description, _user, _meetingTime, _location))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                print('jy',file=sys.stderr)
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getPost')
def getPost():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            cursor.callproc('sp_getPosts')
            posts = cursor.fetchall()

            posts_dict = []
            for post in posts:
                post_dict = {
                    'Id': post[0],
                    'User': post[1],
                    'Headline': post[2],
                    'Description': post[3],
                    'Location': post[4],
                    'PostTime': post[5],
                    'MeetingTime': post[6]
                }
                posts_dict.append(post_dict)

            return json.dumps(posts_dict)
        else:
            print ("poop",sys=stderr)
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug = True)