from collections import defaultdict
import firebase_admin
from flask import Flask, flash, make_response, redirect, render_template, request, url_for
import json
import logging
import pyrebase
import requests
import sys
import time
import os

logging.basicConfig(filename='flask-server.log', level=logging.DEBUG)

config = {
    "apiKey": "AIzaSyC6ce12c32OpCI7-u5ueRbfYhsw_fBnkwk",
    "authDomain": "vip-ipcrowd.firebaseapp.com",
    "databaseURL": "https://vip-ipcrowd.firebaseio.com",
    "storageBucket": "vip-ipcrowd.appspot.com"
}
firebase = pyrebase.initialize_app(config)

#Website: http://127.0.0.1:5000/

''' To do steps:

1) Redo the show_scenario() method to show one indiviudal page
2) move all functionality there
3) create feed page that displays posts
4) add upvote functionality (optional)
5) check the login "no . in username" problem
'''


auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

TOP_N = 3
DEFAULT_PTS = 0

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)


app.config['UPLOAD_FOLDER'] = 'static/Uploads'

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
    print('RECEIVING DATA:', request.form)
    scenario_name = request.form.get('scenario_name', None)
    cur_iter = int(request.form.get('cur_iter', None)) + 1
    hypothesis = request.form.get('hypothesis', None)
    cur_comments = request.form.get('comments', None)
    num_imgs = _get_num_imgs(scenario_name)
    total_points = _get_points()
    uid = _get_uid()
    # if hypothesis:
    #     _store_img_hypothesis(hypothesis, scenario_name, cur_iter)
    if not hypothesis:
        hypothesis = ' '
    if not cur_comments:
        cur_comments = ' '


    if cur_iter != 0:
        print('Storing Scenario Data:', '\n hypothesis:',
         hypothesis, "\n cur_comments:", cur_comments, "\n scenario_name:", scenario_name,
         "\n cur_iter:", cur_iter)

        _store_scenario_data(hypothesis, cur_comments, scenario_name, cur_iter)

    html_page = "scenario.html" # for all other cases
    if scenario_name == "Georgia Tech Disability Services":
        html_page = "upload_image_scenario.html"

    isGTq = False
    if scenario_name == "Georgia Tech Disability Services OLD":
        isGTq = True

    if cur_iter >= num_imgs:
        print('Rerouting to home page')
        if scenario_name == "Georgia Tech Disability Services":
            postTitle = request.form.get('postTitle', None)
            postDesc = request.form.get('postDescription', None)
            postImage = request.form.get('filePath', None)
            handle_postData(postTitle, postDesc, postImage, scenario_name)
            upload_post_image(request.form.get('filePath', None), scenario_name)
        return go_home()

    start_time = time.time()
    img_urls, desc_urls, prompt_urls = _build_url_dict()
    print('_build_url_dict time:  {}'.format(str(time.time() - start_time)))
    img_url = img_urls[scenario_name][cur_iter]
    prompt_url = prompt_urls[scenario_name][cur_iter]
    return render_template(html_page,
        scenario_name=scenario_name, user=uid, cur_iter=cur_iter,
        img_url=img_url, bias='temporary bias', prompt=prompt_url,
        comments=cur_comments, total_points=total_points, isGTq=isGTq)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        print('uploaded filename:', file.filename)
        f_name = file.filename
        local_path_image = os.path.join(app.config['UPLOAD_FOLDER'], f_name)
        file.save(local_path_image)
    return json.dumps({'filename':f_name})


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

def _store_scenario_data(hypothesis, comments, scenario_title, cur_iter):
    id_token = _get_id_token()

    if hypothesis:
        hypo_path = 'users/{uid}/scenario_data/{scenario_title}/hypothesis/{img}'.format(
            uid=_get_uid(),
            scenario_title=scenario_title,
            img=str(int(cur_iter)-1))
        print('Storing hypothesis at:', hypo_path)
        # db.child(hypo_path).set(hypothesis, token=id_token) 
        db.child(hypo_path).set(hypothesis)
    else:
        print('No hypothesis submitted for scenario:', scenario_title)

    if comments:
        comments_path = 'users/{uid}/scenario_data/{scenario_title}/comments/{img}'.format(
            uid=_get_uid(),
            scenario_title=scenario_title,
            img=str(int(cur_iter)-1))
        db.child(comments_path).set(comments, token=id_token) 
        print('Stored comments at:', comments_path)
    else:
        print('No comments submitted for scenario:', scenario_title)


    # db.child('users').child(uid).child('scenario_data').child(scenario_title) \
    #         .child('hypothesis').child(img).set(hypothesis, token=id_token)

    # db.child('users/{uid}/scenario_data/{scenario_title}/hypothesis/{img}'.format(
    #     uid=_get_uid(),
    #     scenario_title=scenario_title,
    #     img=str(int(cur_iter)-1)
    # )).set(hypothesis, token=id_token)

    # db.child('users/{uid}/scenario_data/{scenario_title}/comments/{img}'.format(
    #     uid=_get_uid(),
    #     scenario_title=scenario_title,
    #     img=str(int(cur_iter)-1)
    # )).set(comments, token=id_token)


def _build_url_dict(id_token=None):
    if not id_token:
        id_token = _get_id_token()
    urls = defaultdict(lambda: defaultdict(str))
    description_urls = defaultdict(lambda: defaultdict(str))
    prompt_urls = defaultdict(lambda: defaultdict(str))
    scenarios = db.child('scenario_metadata/scenarios').get(token=id_token)

    scenario_title_list = []
    for scenario in scenarios.each():
        # print("scenario:", scenario.val()['title'], "------------------------------------")
        scenario_title_list.append(scenario.val()['title'])
        urls[scenario.val()['title']] = scenario.val()['images']
        description_urls[scenario.val()['title']] = scenario.val()['description']
        prompt_urls[scenario.val()['title']] = scenario.val()['prompts']
        # print("urls:", urls)
        # print("description_urls", description_urls)
        # print("prompt_urls", prompt_urls)
    print('loaded scenarios:', scenario_title_list)
    return urls, description_urls, prompt_urls


def _get_scenario_urls(token=None):
    img_urls, desc_urls, prompt_urls = _build_url_dict(id_token=token)
    return [(scenario, img_urls[scenario][0], desc_urls[scenario]) for scenario in img_urls]


def upload_post_image(image_path, scenario_title):
    if image_path:
        print('Uploading:', image_path)
        imageName = image_path.split('/')[-1]
        storagePath = 'users/{uid}/{scenario_title}/{img}'.format(
            uid=_get_uid(),
            scenario_title=scenario_title,
            img=imageName
        )
        storage.child(storagePath).put(image_path)
        print("Finished storing user data:", image_path, "at:", storagePath)

        storagePath = 'posts/{scenario_title}/{img}'.format(
            scenario_title=scenario_title,
            img=imageName
        )
        storage.child(storagePath).put(image_path)
        print("Finished storing post data:", image_path, "at:", storagePath)

    else:
        print('no image selected to upload')
        # needs to be implemented


def handle_postData(postTitle, postDesc, image_path, scenario_title):
    if postTitle:
        if not postDesc:
            postDesc = ''

        postData = {
            'postTitle': postTitle,
            'postDesc': postDesc,
            'upvotes': 0,
            'downvotes': 0
        }

        id_token = _get_id_token()

        postKey = db.generate_key() #UNIQUE KEY FOR POST

        postData_path = 'users/{uid}/posts/{scenario_title}/{postKey}'.format(
            uid=_get_uid(),
            scenario_title=scenario_title,
            postKey = postKey
        )
        db.child(postData_path).set(postData, token=id_token) 

        print("Uploaded post data:", postData, "\n post data path:", postData_path)

        #TODO: upload image by calling upload_image method and add new paramter that passes in key
        #that stores storage posts by 'post/{key}imageName.png'

    else:
        print("Can not upload post without a title")




if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)