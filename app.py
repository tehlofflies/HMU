from __future__ import print_function # In python 2.7
import sys

from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash


mysql = MySQL()
app = Flask(__name__)

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
    return render_template('signin.html')


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
            #_hashed_password = generate_password_hash(_password)
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


@app.route('/signIn',methods=['POST','GET'])
def signIn():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _email and _password:

	    	# All Good, let's call MySQL
            conn = mysql.connect()
            cursor = conn.cursor()

            query = "SELECT CheckPassword(%s,%s)"
            cursor.execute(query, (_email,_password))
            data = cursor.fetchall()
            

            if data == 0:
                conn.commit()
                return json.dumps({'message':'User logged in successfully!'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

if __name__ == "__main__":
    app.run()