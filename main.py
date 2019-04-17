from collections import defaultdict
import firebase_admin
from flask import Flask, flash, make_response, redirect, render_template, request, url_for
import json
import logging
import pyrebase
import requests
import sys
import time

logging.basicConfig(filename='flask-server.log', level=logging.DEBUG)

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

TOP_N = 3
DEFAULT_PTS = 0

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

@app.route('/')
@app.route('/login', methods=['POST'])
def login():
    resp = make_response(render_template('login.html', login_error=False))
    resp.set_cookie('idToken', '', expires=0)
    logging.info('Login page loaded')
    return resp


@app.route('/home', methods=['POST'])
def handle_login():
    try:
        email, password = request.form['email'], request.form['password']
        uid = email.split('@')[0]
        user_data = auth.sign_in_with_email_and_password(email, password)
        display_name = db.child('users/{uid}/display_name'.format(uid=uid)).get(
            token=user_data['idToken']).val()
        points = int(db.child('users/{uid}/points'.format(uid=uid)).get(
            token=user_data['idToken']).val())
        scenario_urls = _get_scenario_urls(token=user_data['idToken'])
        rankings = _compute_rankings(display_name=display_name)
    except Exception as e:
        print('Login failed: {}'.format(str(e)))
        return render_template('login.html', login_error=True)
    else:
        resp = make_response(render_template("home.html",
            user=display_name, points=points, rankings=rankings, top_n=TOP_N,
            scenario_urls=scenario_urls))
        resp.set_cookie('idToken', user_data['idToken'])
        return resp


@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')


@app.route('/home%welcome', methods=['POST'])
def handle_signup():
    if request.form['password'] != request.form['confirm_password']:
        logging.info('passwords did not match')
        return redirect('/')
    display_name = '{} {}'.format(request.form['first'], request.form['last'])
    email, password = request.form['email'], request.form['password']
    if '@' not in email or len(password) < 6:
        return render_template('signup.html', signup_error=True)
    uid = email.split('@')[0]
    rankings = _compute_rankings(display_name=display_name)
    user_data = auth.create_user_with_email_and_password(email, password)
    scenario_urls = _get_scenario_urls(token=user_data['idToken'])
    resp = make_response(render_template("home.html",
        user=display_name, points=DEFAULT_PTS, rankings=rankings, top_n=TOP_N,
        scenario_urls=scenario_urls))
    _store_user_info(
        uid, user_data['idToken'], display_name=display_name, email=email,
        points=DEFAULT_PTS)
    resp.set_cookie('idToken', user_data['idToken'])
    return resp


@app.route('/home', methods=['POST'])
def go_home():
    user = _get_display_name()
    uid = _get_uid()
    scenario_urls = _get_scenario_urls()
    rankings = _compute_rankings()
    points = _get_points()
    return render_template('home.html', user=user, points=points,
        rankings=rankings, top_n=TOP_N, scenario_urls=scenario_urls)


@app.route('/signout', methods=['POST'])
def handle_signout():
    resp = make_response(redirect('/'))
    resp.set_cookie('idToken', '', expires=0)
    auth.current_user = None
    return resp


@app.route('/scenario', methods=['POST'])
def show_scenario():
    scenario_name = request.form.get('scenario_name', None)
    cur_iter = int(request.form.get('cur_iter', None)) + 1
    hypothesis = request.form.get('hypothesis', None)
    cur_comments = request.form.get('comments', None)
    num_imgs = _get_num_imgs(scenario_name)
    total_points = _get_points()
    uid = _get_uid()
    # if hypothesis:
    #     _store_img_hypothesis(hypothesis, scenario_name, cur_iter)
    if not cur_comments:
        cur_comments = ''
    if cur_iter >= num_imgs:
        return go_home()
    start_time = time.time()
    img_urls, desc_urls, prompt_urls = _build_url_dict()
    print('_build_url_dict time:  {}'.format(str(time.time() - start_time)))
    img_url = img_urls[scenario_name][cur_iter]
    prompt_url = prompt_urls[scenario_name][cur_iter]
    return render_template("scenario.html",
        scenario_name=scenario_name, user=uid, cur_iter=cur_iter,
        img_url=img_url, bias='temporary bias', prompt=prompt_url,
        comments=cur_comments, total_points=total_points)


def _get_id_token():
    return request.cookies.get('idToken', None)


def _get_user_data():
    id_token = _get_id_token()
    return auth.get_account_info(id_token)


def _get_email():
    return _get_user_data()['users'][0]['email']


def _get_display_name():
    email = _get_email()
    id_token = _get_id_token()
    users = db.child('users').get(token=id_token)
    for user in users.each():
        if user.val()['email'] == email:
            return user.val()['display_name']
    return None


def _get_uid():
    email = _get_email()
    return email.split('@')[0]


def _compute_rankings(display_name=None):
    if not display_name:
        display_name = _get_display_name()
    id_token = _get_id_token()
    rankings = []
    users = db.child('users').get(token=id_token)
    for user in users.each():
        pyre_user = user.val()
        rankings.append((pyre_user['points'], pyre_user['display_name']))
    rankings.sort(key=lambda x: x[0], reverse=True)
    top_rankings = []
    for i, tupl in enumerate(rankings):
        if i < TOP_N or str(tupl[1]) == display_name:
            top_rankings.append((i+1, tupl[0], tupl[1]))
    return top_rankings


def _get_points():
    id_token = _get_id_token()
    uid = _get_uid()
    return int(db.child('users/{uid}/points'.format(uid=uid)).get(
        token=id_token).val())


def _get_num_imgs(scenario_title):
    scenarios = db.child('scenario_metadata/scenarios').get()
    for scenario in scenarios.each():
        if scenario.val()['title'] == scenario_title:
            return len(scenario.val()['images'])
    return -1


def _store_user_info(uid, id_token, display_name=None, email=None, points=None):
    db.child('users/{uid}/display_name'.format(uid=uid)).set(
        display_name, token=id_token)
    db.child('users/{uid}/email'.format(uid=uid)).set(email, token=id_token)
    db.child('users/{uid}/points'.format(uid=uid)).set(points, token=id_token)


def _store_img_hypothesis(hypothesis, scenario_title, cur_iter):
    id_token = _get_id_token()
    db.child('users/{uid}/hypothesis/scenarios/{scenario_title}/{img}'.format(
        uid=_get_uid(),
        scenario_title=scenario_title,
        img=str(int(cur_iter)-1)
    )).set(hypothesis, token=id_token)


def _build_url_dict(id_token=None):
    if not id_token:
        id_token = _get_id_token()
    urls = defaultdict(lambda: defaultdict(str))
    description_urls = defaultdict(lambda: defaultdict(str))
    prompt_urls = defaultdict(lambda: defaultdict(str))
    scenarios = db.child('scenario_metadata/scenarios').get(token=id_token)
    print(scenarios)
    for scenario in scenarios.each():
        urls[scenario.val()['title']] = scenario.val()['images']
        description_urls[scenario.val()['title']] = scenario.val()['description']
        prompt_urls[scenario.val()['title']] = scenario.val()['prompts']
    return urls, description_urls, prompt_urls


def _get_scenario_urls(token=None):
    img_urls, desc_urls, prompt_urls = _build_url_dict(id_token=token)
    return [(scenario, img_urls[scenario][0], desc_urls[scenario]) for scenario in img_urls]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
