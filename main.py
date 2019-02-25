from flask import Flask, flash, redirect, render_template, request, url_for
import json
import logging
import pyrebase
import requests

logging.basicConfig(filename='flask-server.log', level=logging.DEBUG)

config = {
    "apiKey": "AIzaSyC6ce12c32OpCI7-u5ueRbfYhsw_fBnkwk",
    "authDomain": "vip-ipcrowd.firebaseapp.com",
    "databaseURL": "https://vip-ipcrowd.firebaseio.com",
    "storageBucket": "vip-ipcrowd.appspot.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__)

@app.route('/')
@app.route('/login', methods=['POST'])
def login():
	logging.info('Login page loaded')
	return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')

@app.route('/handle_login', methods=['POST'])
def handle_login():
	email, password = request.form['email'], request.form['password']
	logging.info('logging in user with email: {}'.format(email))
	auth.sign_in_with_email_and_password(email, password)
	logging.info('current user data: {}'.format(auth.current_user))
	return render_template("home.html", user=email)
	#TODO(rahulnambiar): handle invalid logins

@app.route('/handle_signup', methods=['POST'])
def handle_signup():
	if request.form['password'] != request.form['confirm_password']:
		logging.info('passwords did not match')
		return redirect('/')
	first, last = request.form['first'], request.form['last']
	user = '{} {}'.format(first, last)
	email, password = request.form['email'], request.form['password']
	logging.info('attempting to create user with email: {} and pass: {}'.format(
		email, password))
	auth.create_user_with_email_and_password(email, password)
	logging.info('user name: {}\ncurrent user data: {}'.format(
		user, auth.current_user))
	return render_template("home.html", user=user)

@app.route('/signout', methods=['POST'])
def handle_signout():
	logging.info('trying to sign out')
	auth.current_user = None
	return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)