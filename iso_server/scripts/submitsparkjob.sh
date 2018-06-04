#!/bin/bash

$SPARK_HOME/bin/spark-submit --py-files $1 --master spark://spark-master:7077 $2 $3 $4 $5
