# IPCrowd

## Overview
This is a prototype designed to showcase the functionalities and interactions of the different modules involved in the application. The web-app can be found [here](https://vip-ipcrowd.herokuapp.com/).

## Software Installation & Setup
Here are installation/set-up instructions for Mac OS X and other UNIX-based operating systems.

### Python/Pip/Virtualenv
1. Make sure python is installed on your machine. You must use python3 in your virtual environment in order to successfully run the scripts. MacOS comes with python installed. In order to check the version of your python, type
   ```
   python --version
   ```
   If you're not currently on Python 3.6.4, upgrade with the following command:
   ```
   brew install python3 && cp /usr/local/bin/python3 /usr/local/bin/python
   ```

2. Install pip with
   ```
   sudo easy_install pip
   ```

3. Install and create a virtual environment. This will allow you to execute any script and locally host the web-app without having to worry about software dependencies.
   
   The following lines of code should set up a virtualenv named vip-venv in your root directory.
   ```
   cd ~/
   pip install virtualenv
   ```
   
### Github
Now we'll get the current version of the code on our local machine. Use Github to maintain version control amongst developers, and to create features without breaking existing code.
Create a folder for the project in your root directory and clone the repository in that folder
   ```
   cd ~/
   mkdir VIP && cd VIP
   git clone https://github.com/carllcox/VIP/
   ```

### Heroku
Create an account on [Heroku](https://heroku.com), and ask Carl to be added to the project as a collaborator.

### Firebase
Create an account on [Firebase](https://firebase.google.com/), and ask Carl to be added to the project as a collaborator.

### Setup Local Development
In order to start developing, the virtual environment needs all necessary dependencies installed, so that your local machine can compile and run the web-app on your localhost.
1. Create and activate your virtual environment
   ```
   cd ~/
   virtualenv vip-venv
   source ./vip-venv/bin/activate
   ```
2. Navigate into your VIP folder and install the specified packages
   ```
   cd ~/VIP
   pip install -r VIP/requirements.txt
   ```
## Tutorials
Here's a description of our tech stack and documentation/tutorials for its elements. Use these for reference - it's easier to learn while doing!

The web-app uses javascript/HTML/CSS for client-side development with Bootstrap for its front-end framework, and python for server-side development with Flask as its micro web framework. It utilizes Firebase, Google's JSON-based NoSQL database, as its data store. The application is deployed on a virtual machine hosted by Heroku.

[Firebase](https://firebase.google.com/docs/web/setup): Firebase is the NoSQL database that we use for our project. All data is stored in JSON format, and can be viewed in firebase's console. 

[Heroku](https://devcenter.heroku.com/articles/getting-started-with-python): Heroku is a cloud platform that allows us to build, run, and operate the application on the cloud. This means we can access the web-app at https://vip-ipcrowd.herokuapp.com/ without having to dedicate a laptop to constantly run the code. Heroku packages all the application's dependencies into one state and then deploys it onto their cloud platform.
## Cycle of Development
Make sure that when you're working on the project, you do the following steps *in order*. This will ensure that we avoid breaking the code or running into merge errors.

Once you've decided on the feature/change to develop - 
1. Pull latest version of the code from Git
   ```
   git pull
   ```
2. Create a new branch for your feature/change and navigate into it
   ```
   git checkout -b branch-name
   ```
3. Activate the virtual environment in order to prepare for development.
   ```
   cd ~/
   source ./vip-venv/bin/activate
   ```
   Sometimes you might need to update the packages in your virtual environment in order to reflect code changes in git. If this is the case, install packages from the requirements file again
   ```
   pip install -r VIP/requirements.txt
   ```
4. Develop the feature and test it on your local machine. You can look at your changes by navigating to the project folder and running Flask on terminal.
   ```
   cd ~/VIP
   python main.py
   ```
   Copy the localhost URL from the bash output and paste it on your browser to see changes. The bash output will look something like this:
   ```
   Running on http://127.0.0.1:5000/
   ```
5. Once you're ready to put your changes up on git, commit your changes to the branch.
   ```
   git commit -a -m "i just added a new feature"
   ```
6. Merge the branch back to master.
   ```
   git checkout master
   git merge branch-name
   ```
7. Remember to deactivate your virtual environment so that you restrict its usage (and the packages you will install on your computer) to the scope of this project. Simply type
   ```
   deactivate
   ```
8. Build and deploy the application on heroku so that your changes reflect on the version available by URL.

## Software Architecture
I've already briefly described the architecture before, but we use Flask as the web framework and most of the front-end development is still in basic js/HTML/CSS. Most back-end and modular development will occur in python since it offers many packages for image and data analysis. Here's an image of how the modules interact with each other:

<img src="https://puu.sh/zwdgI/b1fe2b12be.png" width="600">


Here's how the cloud and database interfaces with the web-application. 

<img src="https://puu.sh/Bn1Zu/1755501795.png" width="400">

## Explanation of Code
Here's an explanation of how the code works (or at least how it works in its current state) - 

i haven't done this part yet :) ;)
