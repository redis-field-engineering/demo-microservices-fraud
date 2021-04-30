#!/usr/bin/env python3

import redis
from os import environ

stream = "CHECK-AI"

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

if environ.get('REDIS_STREAM_GROUP') is not None:
   redis_stream_group = environ.get('REDIS_STREAM_GROUP')
else:
   redis_stream_group = stream

r = redis.Redis(
    host = redis_server,
    port = redis_port,
    password = redis_password,
)

try:
    r.xgroup_create(stream, redis_stream_group, mkstream=True)
except:
    x=1


while True :
    msg = r.xreadgroup(
        redis_stream_group,
        "{}-consumer1".format(redis_stream_group),
        count = 1,
        block = 1000,
        streams={stream: '>'}
    )

    if len(msg) > 0:
        for m in msg:
            msg_id = m[1][0][0].decode('utf-8')
            msg_vals = {k.decode('utf-8'): v.decode('utf-8') for k, v in m[1][0][1].items()}

            #--------------------------------------------------------------------------------
            if msg_vals['user'] != "Guest":
                score = 0.333
                msg_vals['ai_score'] = score
                r.xadd("CART-ADD", msg_vals)
                r.xadd('microservice-logs',
                    {'microservice': 'ai',
                    'user': 'system',
                    'message': "Just a set AI score until we get this working"
                    })
