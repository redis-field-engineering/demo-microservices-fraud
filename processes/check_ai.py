#!/usr/bin/env python3

import redis
from os import environ
import redisai
import numpy as np


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

CATEGORIES = [
 "Apparel", "Automotive", "Baby", "Beauty", "Books", "Camera",
 "Digital_Ebook_Purchase", "Digital_Music_Purchase", "Digital_Software", "Digital_Video_Download", "Digital_Video_Games",
 "Electronics", "Furniture", "Gift_Card", "Grocery", "Health_Personal_Care", "Home_Entertainment",
 "Home_Improvement", "Home", "Jewelry", "Kitchen", "Lawn_and_Garden", "Luggage",
 "Major_Appliances", "Mobile_Apps", "Mobile_Electronics", "Musical_Instruments", "Music", "Office_Products",
 "Outdoors", "PC", "Personal_Care_Appliances", "Pet_Products", "Shoes", "Software", "Sports", "Tools", "Toys", "Video_DVD",
 "Video_Games", "Video", "Watches", "Wireless"
]


r = redisai.Client(
    host = redis_server,
    port = redis_port,
    password = redis_password,
)

try:
    r.xgroup_create(stream, redis_stream_group, mkstream=True)
except:
    x=1

def score_ai(user, category, item_count):
    tnsr_name = "TENSOR:{}:{}:{}".format(user, category, item_count)
    try:
        x = r.hgetall("user:profile:{}".format(user))
        profile = {k.decode('utf-8'): float(v.decode('utf-8')) for k, v in x.items()}
        profile[category] += int(item_count)
        tnsr = []
        for c in CATEGORIES:
            tnsr.append(float(profile[c]))
        r.tensorset(tnsr_name, tnsr, shape=[1, 43],dtype='float')
        profile_results = r.modelrun('classifier_model', tnsr_name, "{}:results".format(tnsr_name))
        res = r.tensorget("{}:results".format(tnsr_name))[0][0]
    except Exception as err:
        print("broken yo", err)
        res = 0.0

    #cleanup any tensors
    r.delete(tnsr_name)
    r.delete("{}:results".format(tnsr_name))

    return("{}".format(res))


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
                score = score_ai(msg_vals['user'], msg_vals['category'], msg_vals['quantity'])
                msg_vals['ai_score'] = score
                r.xadd("CART-ADD", msg_vals)
                r.xadd('microservice-logs',
                    {'microservice': 'ai',
                    'user': 'system',
                    'message': "Just a set AI score until we get this working"
                    })
