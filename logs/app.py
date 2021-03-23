from flask import Flask, render_template, request, redirect 
from flask_bootstrap import Bootstrap
import redis
from os import environ
from datetime import datetime

app = Flask(__name__)

bootstrap = Bootstrap()

def cleanPrefix(mypre):
    if mypre:
        return mypre
    else:
        return ""

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

if environ.get('LOG_FIELDS') is not None:
   log_fields = environ.get('LOG_FIELDS').split(',')
else:
   log_fields = ['microservice', 'user', 'message']



redis = redis.Redis(
   host=redis_server,
   password=redis_password,
   port=redis_port
   )

#================== Start Routes =================================

@app.route('/')
def show_logs():
   lines = []
   logs = redis.xrevrange(log_stream,  max='+', min='-')
   print(logs)
   for log in logs:
      line = [
         datetime.utcfromtimestamp(int(log[0].decode('utf-8').split('-')[0])/1000).isoformat()
         ]
      for f in log_fields:
         line.append(log[1][f.encode('utf-8')].decode('utf-8'))
      lines.append(line)
   return render_template(
      'showlogs.html',
      logs=lines,
      log_fields=log_fields,
      ms_prefix=cleanPrefix(request.headers.get('X-Forwarded-Prefix'))
      )

@app.route('/clean', methods = ['POST'])
def cleanlogs():
   redis.xtrim(log_stream, 0)
   return "<html> <body> <p>Logs have been cleaned.</p><p>You will be redirected in 3 seconds</p> <script> var timer = setTimeout(function() { window.location='%s/' }, 3000); </script> </body> </html>" %(cleanPrefix(request.headers.get('X-Forwarded-Prefix')))

#================== End Routes =================================

if __name__ == '__main__':
    bootstrap.init_app(app)
    app.debug = True
    app.run(port=5019, host="0.0.0.0")
