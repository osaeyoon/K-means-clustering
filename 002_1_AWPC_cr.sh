#!/bin/bash/

START=30
END=70


while [ ${START} -le ${END} ]; do
	awpc_cr=${START}
	export awpc_cr
	python 002_clustering.py
	START=`expr $START + 5`
done
