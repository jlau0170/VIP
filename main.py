from flask import Flask, render_template, redirect, url_for, request
import pyrebase
from cogsci import CogSciModule
import json

config = {
    "apiKey": "AIzaSyC6ce12c32OpCI7-u5ueRbfYhsw_fBnkwk",
    "authDomain": "vip-ipcrowd.firebaseapp.com",
    "databaseURL": "https://vip-ipcrowd.firebaseio.com",
    "storageBucket": "vip-ipcrowd.appspot.com"
}
firebase = pyrebase.initialize_app(config)

app = Flask(__name__)

@app.route('/')
def mainpage():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/<user>', methods=['GET', 'POST'])
def homepage(user=None):
    #test = firebase.database().child("users").child("admin").get().val()
    csm = CogSciModule()
    input_annotations = []
    populated_annos = []
    other_annos = []
    users = firebase.database().child("users").get()
    # print(list(users.val()[user].keys()))
    sample_anno = list(users.val()[user].keys())[0]
    # print(sample_anno)
    source = users.val()[user][sample_anno]['src']
    # print(source)
    for u in users.val():
        # print(type(u))
        # print(user)
        if str(u) == user:
            print("debug")
            for anno in users.val()[u]:
                input_annotations.append(users.val()[u][anno]['text'])

        else:
            for anno in users.val()[u]:
                # print(anno)
                print(users.val()[u][anno]['src'])
                if (source == users.val()[u][anno]['src']):
                    other_annos.append(users.val()[u][anno]['text'])
                populated_annos.append(users.val()[u][anno]['text'])
    print(populated_annos)
    print(input_annotations)
    print(other_annos)
    bias, points = csm.updateCurrentAnnotations(input_annotations)
    return render_template("homepage.html", user=user, bias=bias, points=points, populated_annos=populated_annos)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
