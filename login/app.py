from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_bootstrap import Bootstrap
import redis
from os import environ

# From our local file
from dataload import load_data

app = Flask(__name__,
            static_url_path='/docs',
            static_folder='docs',
)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)

bootstrap = Bootstrap()
#================== Redis Config =================================
if environ.get('REDIS_SERVER') is not None:
   redis_server = environ.get('REDIS_SERVER')
else:
   redis_server = 'localhost'

if environ.get('REDIS_PORT') is not None:
   redis_port = int(environ.get('REDIS_PORT'))
else:
   redis_port = 6379

if environ.get('REDIS_PASSWORD') is not None:
   redis_password = environ.get('REDIS_PASSWORD')
else:
   redis_password = ''

if environ.get('USER_DATA') is not None:
   user_data = environ.get('USER_DATA')
else:
   user_data = './userdata.csv'

if environ.get('LOG_STREAM') is not None:
   log_stream = environ.get('LOG_STREAM')
else:
   log_stream = 'microservice-logs'


redis = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

#================== Start Routes =================================

def cleanPrefix(mypre):
    if mypre:
        return mypre
    else:
        return ""

@app.route('/')
def login():
    if not redis.exists("USER_LIST"):
        load_data(redis_server, redis_port, redis_password, user_data)

    users = []
    for x in redis.smembers("USER_LIST"):
        users.append(x.decode('utf-8'))
    if session.get('username'):
        return render_template(
            'loggedin.html',
            user=session.get('username'),
            ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
            )
    else:
        return render_template(
            'login.html',
            userlist=users,
            ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
            )

@app.route('/dologin', methods = ['POST'])
def dologin():
        form = request.form.to_dict()
        session['username'] = form['user']
        redis.xadd(log_stream, {"microservice": "login", "user": form['user'], "message": "%s has logged in" %(form['user'])})
        return render_template(
           'loggedin.html',
           user=session.get('username'),
           ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
           )

@app.route('/logout')
def dologout():
    username = request.args.get('user')
    session.clear()
    redis.xadd(log_stream, {"microservice": "login", "user": username, "message": "%s has logged out" %(username)})
    return "<html> <body> <p>%s has logged out.</p><p>You will be redirected in 3 seconds</p> <script> var timer = setTimeout(function() { window.location='%s/' }, 3000); </script> </body> </html>" %(username, cleanPrefix(request.headers.get('X-Forwarded-Prefix')))

#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    bootstrap.init_app(app)
    sess.init_app(app)
    app.debug = True
    app.run(port=5011, host="0.0.0.0")
