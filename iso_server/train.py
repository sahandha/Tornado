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
sc = SparkContext(appName="Isolation Forest")

def main(file, savepath):

    X = np.genfromtxt(file, delimiter=',')
    data_RDD = sc.parallelize(partition(X,int(len(X)/8)))
    Forest = data_RDD.map(lambda x: iso.iForest(x,ntrees=100, sample_size=256))
    save_object(Forest.collect(),savepath+"/trees")

def partition(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    datafile = sys.argv[1]
    savepath = sys.argv[2]
    main(datafile, savepath)
