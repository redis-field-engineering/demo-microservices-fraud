from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
import redis
import json
import hashlib

app = Flask(__name__,
            static_url_path='/docs',
            static_folder='docs',
)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)

bootstrap = Bootstrap()

nav = Nav()
topbar = Navbar('',
    View('Home', 'index'),
)

#================== Start Routes =================================

@app.route('/')
def index():
    if session.get('username'):
        session['foo'] = "bar"
        return json.dumps({
                    "agent": hashlib.md5(request.headers.get('User-Agent').encode()).hexdigest(),
                    "client": request.remote_addr,
                    "session": session.get('foo'),
                    "sid": session.sid,
                    "username": session.get('username')
                    })
    else:
        return redirect("/login", code=302)

@app.route('/login')
def login():
    session['username'] = "chris"
    return "LOGIN GOES HERE"

#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    bootstrap.init_app(app)
    sess.init_app(app)
    nav.init_app(app)
    app.debug = True
    app.run(port=5010, host="0.0.0.0")




