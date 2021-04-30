#!/usr/bin/env python3

from redisearch import Client, Query
from os import environ

stream = "CART-ADD"

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

r = Client(
   'ShoppingCart',
    host = redis_server,
    port = redis_port,
    password = redis_password,
)

try:
    r.redis.xgroup_create(stream, redis_stream_group, mkstream=True)
except:
    x=1


while True :
    msg = r.redis.xreadgroup(
        redis_stream_group,
        "{}-consumer1".format(redis_stream_group),
        count = 1,
        block = 1000,
        streams={stream: '>'}
    )

    if len(msg) > 0:
        for m in msg:
            msg_id = m[1][0][0]
            msg_vals = {k: v for k, v in m[1][0][1].items()}

            #--------------------------------------------------------------------------------
            r.redis.hset("SHOPPING_CART:{}".format(msg_vals['cart_id']), mapping=msg_vals)
            # rescore the cart
            scorehash = {'items': 0, 'score': 100, 'scores': [] }
            itemcount = 0
            query = Query("@session:{}".format(msg_vals['session'])).paging(0, 500)
            items = r.search(query).docs
            for item in items:
               scorehash['items'] += 1
               scorehash['scores'].append(int(100*(float(item.ai_score) + float(item.identity_score) + float(item.profile_score)/2)))

            if scorehash['items'] > 0:
               scorehash['score'] = 100 - min(scorehash['scores'])
            
            del scorehash['scores']
            r.redis.hset("CART_SCORE:{}".format(msg_vals['session']), mapping=scorehash)
            
            r.redis.xadd('microservice-logs',
               {'microservice': 'cart',
               'user': 'system',
               'message': "User: %s added item: %s to cart" %( msg_vals['user'], msg_vals['product_name'] )
               })
