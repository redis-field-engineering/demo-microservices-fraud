#!/bin/bash -e

http :8001/config config=@kong.yml

cat AI/classifier_model.pb | redis-cli -x AI.MODELSET classifier_model TF CPU INPUTS x OUTPUTS Identity BLOB

http :8000/login 
http :8000/cart 
