#!/usr/bin/env python

import redisai
import numpy as np
from ml2rt import load_model

conn = redisai.Client()

tf_model = load_model('./classifier_model.pb')

conn.tensorset('x_valid',
        [0, 0, 0, 0, 1, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        shape=[1, 43],
        dtype='float')

conn.tensorset('x_fraud',
        [0, 0, 2, 0, 1, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        shape=[1, 43],
        dtype='float')

profile_model = conn.modelset(
    'profile_model', 'tf', 'cpu',
    inputs=['x'], outputs=['Identity'], data=tf_model)

valid_profile_results = conn.modelrun('profile_model', 'x_valid', 'x_valid_results')
fraud_profile_results = conn.modelrun('profile_model', 'x_fraud', 'x_fraud_results')

valid_res = conn.tensorget('x_valid_results')
fraud_res = conn.tensorget('x_fraud_results')

print("Valid Score: {} -- Fraud Score: {}".format(valid_res[0][0], fraud_res[0][0]))
