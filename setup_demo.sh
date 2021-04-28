#!/bin/bash -ex

http :8001/config config=@kong.yml

for i in `ls gears/*.py`; do
	SCRIPT=`basename ${i}`
	echo "Loading ${SCRIPT}"
	redis-cli RG.PYEXECUTE "$(cat $i)"

done

