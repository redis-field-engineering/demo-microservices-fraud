#!/usr/bin/env python3

import redis
from os import environ

stream = "CHECK-IDENTITY"

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
            # if not guest checks Identity of user
            if msg_vals['action'] == "enhance" and msg_vals['user'] != "Guest":
                score = 0.0
                if int(r.exists("Identity:{}:IPS".format(msg_vals['user']))) > 0:
                    score += r.sismember("Identity:{}:IPS".format(msg_vals['user']), msg_vals['ipaddr'])
                if int(r.exists("Identity:{}:BrowserFingerprint".format(msg_vals['user']))) > 0:
                    score += r.sismember("Identity:{}:BrowserFingerprint".format(msg_vals['user']), msg_vals['fingerprint'])

                msg_vals['identity_score'] = "%.2f" %(score/2.0)
                if not 'cart_id' in msg_vals:
                    msg_vals['cart_id'] =  msg_id
                del msg_vals['action']
                r.xadd('CHECK-PROFILE', msg_vals)
                r.xadd('microservice-logs',
                    {'microservice': 'identity',
                    'user': 'system',
                    'message': "Check identity for user: %s , result: %f"  %(msg_vals['user'], score/2.0)
                    })
            # Update the user if not guest
            elif  msg_vals['action'] == "update" and msg_vals['user'] != "Guest":
                if 'ipaddr' in msg_vals:
                    r.sadd("Identity:{}:IPS".format(msg_vals['user']), msg_vals['ipaddr'])
                if 'fingerprint' in msg_vals:
                    r.sadd("Identity:{}:BrowserFingerprint".format(msg_vals['user']), msg_vals['fingerprint'])
                r.xadd('microservice-logs',
                    {'microservice': 'identity',
                    'user': 'system',
                    'message': "Updated Identity for user: %s"  %(msg_vals['user'])
                    })
            # If guest go straight to cart
            elif  msg_vals['user'] == "Guest":
                msg_vals['profile_score'] = "0"
                msg_vals['identity_score'] = "0"
                msg_vals['ai_score'] = "0"
                if not 'cart_id' in msg_vals:
                    msg_vals['cart_id'] =  msg_id
                del msg_vals['action']
                r.xadd('CART-ADD', msg_vals)
                r.xadd('microservice-logs',
                    {'microservice': 'identity',
                    'user': 'system',
                    'message': "%s user: going directly to cart" %( msg_vals['user'])
                    })
            else:
                r.xadd('microservice-logs',
                    {'microservice': 'identity',
                    'user': 'system',
                    'message': "Invalid action: %s or user: %s" %( msg_vals['action'], msg_vals['user'])
                    })