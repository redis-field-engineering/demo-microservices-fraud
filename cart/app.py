from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from redisearch import Client, Query, NumericFilter
from redisbloom.client import Client as RB

import redis
from os import environ

# From our local file
from dataload import load_data
from dataload import cart_score

app = Flask(__name__,
            static_url_path='/images',
            static_folder='images',
)

SESSION_TYPE = 'redis'
app.config.from_object(__name__)

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

if environ.get('LOG_STREAM') is not None:
   log_stream = environ.get('LOG_STREAM')
else:
   log_stream = 'microservice-logs'


redis = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

client = Client(
   'ShoppingCart',
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

rb = RB(
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

@app.route('/', methods=['GET'])
def catalog():
   if not session.get("username"):
      session['username'] = 'Guest'

   if request.args.get('details'):
      details = True
   else:
      details = False

   entries = []
   try:
      client.info()
   except:
      load_data(redis_server, redis_port, redis_password)
      redis.xadd(log_stream, {"microservice": "cart", "user": "system", "message": "loaded cart data"})

   query = Query(session.sid.replace("-", "")).limit_fields("session").verbatim().paging(0, 50)
   items = client.search(query).docs
   fraudscore = 100
   carttotal = 0.00
   for item in items:
      entries.append(item.__dict__)
      carttotal += float(item.__dict__["unit_price"])*int(item.__dict__["quantity"])



   tginfo = cart_score(redis_server, redis_port, redis_password, session.sid.replace("-", ""))
   
   return render_template(
      'cart.html',
      entries = entries,
      details = details,
      carttotal = carttotal,
      fraudscore = tginfo[1],
      cart_count = tginfo[0],
      ms_prefix = cleanPrefix(request.headers.get('X-Forwarded-Prefix')),
      username = session.get("username"),
      )

@app.route('/checkout', methods=['POST'])
def checkout():
   query = Query(session.sid.replace("-", "")).limit_fields("session").paging(0, 50)
   items = client.search(query).docs
   for item in items:
      rb.bfAdd("BFPROFILE:%s:%s" % (item.category, item.level), item.user )
      rb.bfAdd("BFPROFILE:Category:%s" %(item.category), item.user)
      redis.xadd(log_stream, {
         "microservice": "cart",
         "user": item.user,
         "message": "purchased quantity:{} item{}".format(item.quantity, item.product_name)})

      redis.unlink(item.id)

   return "<html> <body> <h2>Thanks for your purchase!</h2><script> var timer = setTimeout(function() { window.location='/' }, 700); </script> </body> </html>" 

#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    sess.init_app(app)
    app.debug = True
    app.run(port=5018, host="0.0.0.0")
