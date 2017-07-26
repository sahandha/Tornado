#!/bin/bash

$SPARK_HOME/bin/spark-submit --py-files $2 --master spark://spark-master:7077 $ISOFOREST/isoforestcalls.py $1
