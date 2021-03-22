from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
import redis
import json
import hashlib
from os import environ

app = Flask(__name__,
            static_url_path='/docs',
            static_folder='docs',
)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)

if environ.get('TOP_URL') is not None:
   top_url = environ.get('TOP_URL')
else:
   top_url = ""

bootstrap = Bootstrap()

nav = Nav()
topbar = Navbar('',
    View('Home', 'index'),
)

#================== Start Routes =================================

@app.route('/login')
def login():
    if session.get('username'):
        return "Logged in as %s" %session.get('username')
    else:
        return "LOGIN GOES HERE"

#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    bootstrap.init_app(app)
    sess.init_app(app)
    nav.init_app(app)
    app.debug = True
    app.run(port=5011, host="0.0.0.0")
