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

#nav = Nav()
#topbar = Navbar('',
#    View('Login', 'login'),
#    View('Logout', 'dologout'),
#)
#nav.register_element('top', topbar)


bootstrap = Bootstrap()

#================== Start Routes =================================

def cleanPrefix(mypre):
    if mypre:
        return mypre
    else:
        return ""

@app.route('/')
def login():
    if session.get('username'):
        return render_template(
            'loggedin.html',
            user=session.get('username'),
            ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
            )
    else:
        return render_template(
            'login.html',
            userlist={'chris@example.com': 2112, 'reiko@example.com': 2111},
            ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
            )

@app.route('/dologin', methods = ['POST'])
def dologin():
        form = request.form.to_dict()
        session['username'] = form['user']
        return render_template('loggedin.html', user=session.get('username'))

@app.route('/logout')
def dologout():
    username = request.args.get('user')
    session.clear()
    return "<html><head><meta http-equiv=\"refresh\" content=\"5;url=%s\"/></head>logged out %s</html}" %(cleanPrefix(request.headers.get('X-Forwarded-Prefix')),username)

#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    bootstrap.init_app(app)
#    nav.init_app(app)
    sess.init_app(app)
    app.debug = True
    app.run(port=5011, host="0.0.0.0")
