#!/bin/bash -ex

http :8001/config config=@kong.yml

for i in `ls gears/*.py`; do
	SCRIPT=`basename ${i}`
	echo "Loading ${SCRIPT}"
	redis-cli RG.PYEXECUTE "$(cat $i)"

done

redis-cli BF.ADD BFPROFILE:Kitchen:bargain chris@example.com
redis-cli BF.ADD BFPROFILE:Category:Kitchen chris@example.com
