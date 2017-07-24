#!/bin/bash

$SPARK_HOME/spark-submit --master spark://spark-master:7077 $ISOFOREST/scripts/isoforestcalls.py $1
