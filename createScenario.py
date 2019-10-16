#used to submit scenarios to the firebase
import pyrebase
import json

config = {
    "apiKey": "AIzaSyC6ce12c32OpCI7-u5ueRbfYhsw_fBnkwk",
    "authDomain": "vip-ipcrowd.firebaseapp.com",
    "databaseURL": "https://vip-ipcrowd.firebaseio.com",
    "storageBucket": "vip-ipcrowd.appspot.com"
}
firebase = pyrebase.initialize_app(config)

db = firebase.database()


#storage loc: gs://vip-ipcrowd.appspot.com/images/scenario0/00-01.jpg
#images:
image_0 = 'https://firebasestorage.googleapis.com/v0/b/vip-ipcrowd.appspot.com/o/images%2Fscenario0%2F00-01.jpg?alt=media&token=4e54c5fc-8b11-4253-bde5-e0ebdff9d75e'

#prompts:
prompt_0 = """Georgia Tech would like to make changes to the physical layout
of the Georgia Tech campus in order to facilitate an easier campus for those
in need. Georgia Tech needs help in identifying places on campus that
need physical changes. Which places on campus require changes? Enter the 
name of a building/walkway/etc in the text box below and annotate the image
below for larger areas."""


# data = {"name": "Mortimer 'Morty' Smith"}
# db.child("users").child("Morty").set(data)

author = "abdullah"
description = """Georgia Tech would like to make changes to the physical layout
of the campus in order to facilitate an easier campus for those
in need. Georgia Tech needs help in identifying places on campus that
need physical changes. Help them identify and pinpoint specific places that
could benefit from these changes."""
images = {0: image_0}
prompts = {0: prompt_0}

title = "Georgia Tech Disability Services"

data = {
	"author": author,
	"description": description,
	"images": images,
	"prompts": prompts,
	"title": title
}

# --- Download current scenarios to scenario_data
# scenario_data = db.child("scenario_metadata").get().val()


# --- Store scenario data into scenario_data.json
# with open('scenario_data.json', 'w') as fp: 
# 	json.dump(scenario_data, fp, sort_keys=True, indent=4)


# --- Read scenario data from scenario_data.json

scenario_data = {}
with open('scenario_data.json', 'r') as fp2: 
    scenario_data = json.load(fp2)

# print(data2)


# --- Upload data


print("uploading scenario data")
db.child("scenario_metadata").set(scenario_data)
print("finished scenario data")