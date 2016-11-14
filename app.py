from __future__ import print_function # In python 2.7
import sys
import datetime
import time

from flask import Flask, render_template, json, request, redirect, session, jsonify, flash, Response
from flaskext.mysql import MySQL

from flask_wtf import Form
from wtforms import DateField
from datetime import date

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


@app.route('/signUp',methods=['POST'])
def signUp():
	try:
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _email and _password:
			
			if "@" not in _email:
				return render_template('error.html', error = 'Invalid email')

			# All Good, let's call MySQL
			
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_createUser',(_name,_email,_password))
			data = cursor.fetchall()

			if len(data) is 0:
				conn.commit()
				return render_template('error.html', error = 'User created successfully.')
			else:
				flash(str(data[0]), category='error')
				return redirect('showSignUp')
		else:
			flash("Enter the required fields", category='error')
			return redirect('/showSignUp')
		cursor.close()
		conn.close()

	except Exception as e:
		flash(str(e), category='error')
		return redirect('/showSignUp')

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
				return render_template('error.html', error = 'Password is not correct.')
		else:
			return render_template('error.html', error = 'Email address does not exist.')
		cursor.close()
		con.close()

	except Exception as e:
		return render_template('error.html',error = str(e))
		
@app.route('/showAddPost')
def showAddPost():
	form = DateForm()
	#if form.validate_on_submit():
	#    return form.dt.data.strftime('%x')
	#return render_template('addPost.html')
	return render_template('addPost.html', form=form)

@app.route('/addPost',methods=['POST'])
def addPost():
	conn = mysql.connect()
	cursor = conn.cursor()
	try:
		if session.get('user'):
			_headline = request.form['inputHeadline']

			if 'inputDescription' in request.form:
				_description = request.form['inputDescription']
			else:
				_description = ""

			if 'inputMeetingDate' in request.form:
				_unformattedDate = request.form['inputMeetingDate']
			else: 
				form = DateForm(request.form)
				_unformattedDate = form.dt.data.strftime('%x')
			
			_formattedDate = datetime.datetime.strptime(_unformattedDate, '%m/%d/%y')
			#print(_formattedDate, file=sys.stderr)

			_user = session.get('user')
			_unformattedTime = request.form['inputMeetingTime']
			
			#formattedTime = datetime.time(*map(int, _unformattedTime.split(':')))
			formattedTime = datetime.datetime.strptime(_unformattedTime, '%H:%M').time()
			
			_formattedDatetime = datetime.datetime.combine(_formattedDate, formattedTime)

			if(_formattedDatetime < datetime.datetime.today()): 
				flash("Date/Time must be in future", category='error')
				return redirect('/showAddPost')
			
			_location = request.form['inputLocation']
			cursor.callproc('sp_addPost',(_headline, _description, _user, _formattedDatetime, _location))
			data = cursor.fetchall()

			if len(data) is 0:
				conn.commit()
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
					'User': "WHO: "+post[1],
					'Headline': post[2],
					'Description': "WHAT'S UP: "+post[3],
					'Location': "WHERE: "+post[4],
					'MeetingTime': "WHEN: "+post[6].strftime("%B %d, %Y, %I:%M %p"),
					'PostTime': "Posted: "+post[5].strftime("%B %d, %Y, %I:%M %p")
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