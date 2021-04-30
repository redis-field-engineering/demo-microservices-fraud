#!/bin/bash -ex

http :8001/config config=@kong.yml

for i in `ls gears/*.py`; do
	SCRIPT=`basename ${i}`
	echo "Loading ${SCRIPT}"
	redis-cli RG.PYEXECUTE "$(cat $i)" REQUIREMENTS numpy

done

cat AI/classifier_model.pb | redis-cli -x AI.MODELSET classifier_model TF CPU INPUTS x OUTPUTS Identity BLOB

http :8000/login 
http :8000/cart 
