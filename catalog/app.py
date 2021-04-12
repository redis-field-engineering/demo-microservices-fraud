from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from redisearch import Client, Query, NumericFilter
import redis
import hashlib
from os import environ

# From our local file
from dataload import load_data

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

if environ.get('NEXT_STAGE') is not None:
   next_stream = environ.get('NEXT_STAGE')
else:
   next_stream = 'CHECK-IDENTITY'


redis = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

client = Client(
   'Catalog',
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

@app.route('/', methods=['GET', 'POST'])
def catalog():
   if not session.get("username"):
      session['username'] = 'Guest'

   entries = []
   try:
      client.info()
   except:
      load_data(redis_server, redis_port, redis_password)
      redis.xadd(log_stream, {"microservice": "catalog", "user": "system", "message": "loaded catalog data"})
   if request.method == 'GET':
      query = Query('*').paging(0, 50)
   else:
      fm = request.form.to_dict()
      if fm['search'] == "":
         term = '*'
      else:
         term = fm['search']
      query = Query(term).paging(0, 50)

   items = client.search(query).docs
   for item in items:
      entries.append(item.__dict__)
   
   return render_template(
      'catalog.html',
      entries = entries,
      ms_prefix = cleanPrefix(request.headers.get('X-Forwarded-Prefix')),
      username = session.get("username"),
      fraudscore = "100"
      )

@app.route('/purchase', methods=['POST'])
def purchase():
   fm = request.form.to_dict()
   item = client.search(Query('*').add_filter(NumericFilter('product_id', int(fm['item']), int(fm['item'])))).docs[0].__dict__
   msg = {
      "quantity": fm['quantity'],
      "product_id": item['product_id'],
      "product_name": item['product'],
      "category": item['category'],
      "level": item['level'],
      "unit_price": item['price'],
      "user": session.get('username'),
      "action": "enhance",
      "ipaddr": request.remote_addr,
      "fingerprint": hashlib.md5(request.headers.get('User-Agent').encode('utf-8')).hexdigest(),
      "session": session.sid.replace("-", ""),
   }
   redis.xadd(log_stream, 
   {
      "microservice": "catalog",
      "user": session.get('username'),
      "message": "added to cart $%.2f" %(float(item['price'])*int(fm['quantity']))
   })
   redis.xadd(next_stream, msg)
   return "<html><body><script> var timer = setTimeout(function() { window.location='%s/' }, 5); </script> </body> </html>" %(cleanPrefix(request.headers.get('X-Forwarded-Prefix')))


#================== End Routes =================================

if __name__ == '__main__':
    sess = Session(app)
    sess.init_app(app)
    app.debug = True
    app.run(port=5015, host="0.0.0.0")
