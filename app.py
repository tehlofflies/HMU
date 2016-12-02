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

@app.route('/showEditProfile')
def showEditProfile():
	if session.get('user'):
		_id = session.get('user')
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_getProfile', str(_id))
		#cursor.execute("SELECT * FROM tbl_user WHERE user_id=" + str(_id))
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

		return render_template('editprofile.html', name=_name, description=_description, email=_email, phone=_phone, facebook=_facebook)
	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/editProfile',methods=['POST'])
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
			#cursor.execute("UPDATE tbl_profile SET profile_name='" + _name + "',profile_bio='" + _description + "',profile_phone='" + _phone + "',profile_facebook='" + _facebook + "' WHERE profile_id='" + str(_id) + "';")
			conn.commit()
			#cursor.execute("UPDATE tbl_profile SET profile_name = %s WHERE profile_username = %s;" % (_name, _email))
			return redirect('/me')
	except Exception as e:
		return render_template('error.html', error = str(e))
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
			cursor.callproc('sp_getProfile', (_user,))
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
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))

@app.route('/user/<user_id>')
def user(user_id):
	conn = mysql.connect()
	cursor = conn.cursor()
	try:
		if session.get('user'):
			cursor.callproc('sp_getProfile', (user_id,))
			infos = cursor.fetchall()

			for info in infos:
				name = info[1]
				bio = info[2]
				email = info[3]
				phone = info[4]
				fb = info[5]

			return render_template('userProfile.html', 
				me = 0,
				user_id = user_id, 
				name = name,
				bio = bio,
				email = email,
				phone = phone,
				fb = fb
			)
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))


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
		if _name and _email and _password and not _name.isspace() and not _password.isspace():

			if "@" not in _email:
				flash("Invalid email", category='error')
				return redirect('/showSignUp')
				# return render_template('error.html', error = 'Invalid email')

			# All Good, let's call MySQL

			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_createUser',(_name,_email,_password))
			data = cursor.fetchall()

			if len(data) is 0:
				# user signed up successfully
				conn.commit()

				# sign the user in/get user session
				cursor.callproc('sp_validateLogin', (_email,))
				data1 = cursor.fetchall()
				session['user'] = data1[0][0]
				print(data1[0][0], file=sys.stderr)

				# create a user profile
				cursor.callproc('sp_createProfile', (_name,None,_email,None,None))
				data2 = cursor.fetchall()

				if len(data2) is 0:
					conn.commit()
					return redirect('/showEditProfile') 
				else:
					return render_template('error.html',error = 'An error occurred!')

				#return render_template('error.html', error = 'User created successfully.')
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

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
	try:
		_username = request.form['inputEmail']
		_password = request.form['inputPassword']
	   
		if _username and _password and not _password.isspace():
			# connect to mysql
			con = mysql.connect()
			cursor = con.cursor()
			cursor.callproc('sp_validateLogin',(_username,))
			data = cursor.fetchall()

			if len(data) > 0:
				if str(data[0][3])==_password:
					session['user'] = data[0][0]
					print(data[0][0], file=sys.stderr)
					return redirect('/showEditProfile')
				else:
					flash("Password is not correct", category='error')
					return redirect('/showSignIn')
					# return render_template('error.html', error = 'Password is not correct.')
			else:
				flash("Email address does not exist", category='error')
				return redirect('/showSignIn')
				# return render_template('error.html', error = 'Email address does not exist.')
			cursor.close()
			con.close()

		else:
			flash("Enter the required fields", category='error')
			return redirect('/showSignIn')

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
			
			#print(_formattedDate, file=sys.stderr)

			_user = session.get('user')
			_unformattedTime = request.form['inputMeetingTime']
			
			#formattedTime = datetime.time(*map(int, _unformattedTime.split(':')))
			
			if _headline and not _headline.isspace() and _location and not _location.isspace() and _unformattedTime is not None and _unformattedDate is not None:
				_formattedDate = datetime.datetime.strptime(_unformattedDate, '%m/%d/%y')
				formattedTime = datetime.datetime.strptime(_unformattedTime, '%H:%M').time()
				_formattedDatetime = datetime.datetime.combine(_formattedDate, formattedTime)

				if(_formattedDatetime < datetime.datetime.today()): 
					flash("Date/Time must be in future", category='error')
					return redirect('/showAddPost')
				
				
				cursor.callproc('sp_addPost',(_headline, _description, _user, _formattedDatetime, _location))
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