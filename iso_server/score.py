import matplotlib
matplotlib.use('Agg')

import sys
import iso_forest as iso
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np

try:
    import cPickle as pickle
except:
    import pickle

import findspark
findspark.init()

from pyspark import SparkContext, SparkConf

# Note since we will be using spark-submit to submit the job, we don't need to define conf.
# conf = SparkConf().setAppName("iso_forest").setMaster("local[*]")
sc = SparkContext(appName="Isolation Forest Score")

def main(X, file, savepath, imagepath):
    n = 8
    X = FormatData(X)
    traineddata = load_object(file)
    data_RDD = sparkify_data(traineddata,n)

    S_t = data_RDD.map(lambda F: F.compute_paths([X]))
    S   = S_t.reduce(lambda a,b: a+b)/n

    print("Successfully score and the score is:", S)

def partition(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]


def load_object(filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        trees = pickle.load(output, pickle.HIGHEST_PROTOCOL)

def sparkify_data(list, n):
    pl = partition(list,n)
    rdd = sc.parallelize(pl)
    return rdd

def FormatData(X):
    datapoint = [float(x) for x in X.strip('()').split(',')]
    return datapoint

if __name__=="__main__":
    X         = sys.argv[1]
    datafile  = sys.argv[2]
    savepath  = sys.argv[3]
    imagepath = sys.argv[4]
    main(X, datafile, savepath, imagepath)
