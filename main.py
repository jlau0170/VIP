from collections import defaultdict
from firebase_admin import credentials
from flask import Flask, flash, redirect, render_template, request, url_for
import json
import logging
import pyrebase
import requests

logging.basicConfig(filename='flask-server.log', level=logging.DEBUG)

cred = credentials.Certificate('vip-ipcrowd-firebase-adminsdk-4mwoc-5aa0f5640e.json')
config = {
    "apiKey": "AIzaSyC6ce12c32OpCI7-u5ueRbfYhsw_fBnkwk",
    "authDomain": "vip-ipcrowd.firebaseapp.com",
    "databaseURL": "https://vip-ipcrowd.firebaseio.com",
    "storageBucket": "vip-ipcrowd.appspot.com"
}
firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

def _get_image_urls():
    img_urls = defaultdict(lambda: defaultdict(str))
    num_scenarios = int(db.child('scenario_metadata/num_scenarios').get().val())
    for i in range(num_scenarios):
        scenario_name = 'scenario_{}'.format(i+1)
        db_path = 'scenario_metadata/scenarios/{}/'.format(scenario_name)
        num_imgs = int(db.child(db_path + 'num_imgs').get().val())
        title = str(db.child(db_path + 'title').get().val())
        for j in range(num_imgs):
            url_path = 'scenario_metadata/scenarios/{scenario}/images/{cur_img}'.format(
                scenario=scenario_name, cur_img=j)
            url = db.child(url_path).get().val()
            img_urls[title][j] = str(url)
    logging.info('img_urls: {}'.format(str(img_urls)))
    return img_urls

def _get_num_imgs(scenario_title):
    num_scenarios = int(db.child('scenario_metadata/num_scenarios').get().val())
    for i in range(num_scenarios):
        scenario_name = 'scenario_{}'.format(i+1)
        db_path = 'scenario_metadata/scenarios/{}/'.format(scenario_name)
        title = str(db.child(db_path + 'title').get().val())
        if title == scenario_title:
            return int(db.child(db_path + 'num_imgs').get().val())
    return -1

def _get_scenario_urls():
    return [(scenario, img_urls[scenario][0]) for scenario in img_urls]

img_urls = _get_image_urls()


app = Flask(__name__)


@app.route('/')
@app.route('/login', methods=['POST'])
def login():
    logging.info('Login page loaded')
    return render_template('login.html')


@app.route('/home', methods=['POST'])
def handle_login():
    email, password = request.form['email'], request.form['password']
    uid = email.split('@')[0]
    user = db.child('users/{}/display_name'.format(uid)).get().val()
    auth.sign_in_with_email_and_password(email, password)
    TOP_N = 3
    rankings = _get_rankings(user, TOP_N)
    logging.info('rankings: {}'.format(rankings))
    points = _get_points(uid)
    scenario_urls = _get_scenario_urls()
    logging.info('logging in user with email: {}'.format(email))
    logging.info('current user data: {}'.format(auth.current_user))
    logging.info('scenario_urls: {}'.format(str(scenario_urls)))
    return render_template("home.html",
        user=user, points=points, rankings=rankings, top_n=TOP_N,
        scenario_urls=scenario_urls)
    #TODO(rahulnambiar): handle invalid logins


@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')


@app.route('/home%welcome', methods=['POST'])
def handle_signup():
    if request.form['password'] != request.form['confirm_password']:
        logging.info('passwords did not match')
        return redirect('/')
    first, last = request.form['first'], request.form['last']
    user = '{} {}'.format(first, last)
    uid = email.split('@')[0]
    TOP_N = 3
    points = 0
    email, password = request.form['email'], request.form['password']
    logging.info('attempting to create user with email: {} and pass: {}'.format(
    email, password))
    auth.create_user_with_email_and_password(email, password)
    logging.info('user name: {}\ncurrent user data: {}'.format(
    user, auth.current_user))
    db.child('users/{}/display_name'.format(uid)).set(user)
    db.child('users/{}/email'.format(uid)).set(email)
    db.child('users/{}/points'.format(uid)).set(points)
    rankings = _get_rankings(user, 3)
    scenario_urls = _get_scenario_urls()
    return render_template("home.html",
        user=user, points=points, rankings=rankings, top_n=TOP_N,
        scenario_urls=scenario_urls)


@app.route('/home', methods=['POST'])
def go_home():
    user = _get_display_name(auth.current_user['email'])
    scenario_urls = _get_scenario_urls()
    return render_template('home.html', user=user, scenario_urls=scenario_urls)


@app.route('/signout', methods=['POST'])
def handle_signout():
    logging.info('trying to sign out')
    auth.current_user = None
    return redirect('/')


@app.route('/scenario', methods=['POST'])
def show_scenario():
    logging.info('API request form: {}'.format(str(request.form)))
    scenario_name = request.form.get('scenario_name', None)
    cur_iter = int(request.form.get('cur_iter', None)) + 1
    db_path = 'scenario_metadata/scenarios/{}/num_imgs'.format(scenario_name)
    num_imgs = _get_num_imgs(scenario_name)
    if cur_iter < num_imgs:
        img_url = img_urls[scenario_name][cur_iter]
        return render_template("scenario.html",
            scenario_name=scenario_name, cur_iter=cur_iter,
            img_url=img_url, bias='temporary bias')
    return go_home()
    # return render_template("scenario.html",
    #     title=title, info=info, question=question, points=points,
    #     img_src=img_src)


def _get_display_name(email):
    users = db.child('users').get()
    for user in users.each():
        if user.val()['email'] == email:
            return user.val()['display_name']
    return None


def _get_rankings(display_name, top_n):
    rankings = []
    users = db.child('users').get()
    for user in users.each():
        pyre_user = user.val()
        logging.info('pyre_user: {}'.format(pyre_user))
        rankings.append((pyre_user['points'], pyre_user['display_name']))
    rankings.sort(key=lambda x: x[0], reverse=True)
    top_rankings = []
    for i, tupl in enumerate(rankings):
        if i < top_n or str(tupl[1]) == str(display_name):
            top_rankings.append((i+1, tupl[0], tupl[1]))
    return top_rankings


def _get_points(uid):
    return int(db.child('users/{}/points'.format(uid)).get().val())


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
