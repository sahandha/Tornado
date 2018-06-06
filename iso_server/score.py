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

def main(X, datafile, savepath, imagepath):
    n = 8
    X = FormatData(X)
    traineddata = load_object(savepath+'/trees')
    data_RDD    = sparkify_data(traineddata,n)

    S_t = data_RDD.map(lambda F: F.compute_paths([X]))
    S   = S_t.reduce(lambda a,b: a+b)/n
    scores = oad_object(savepath+'/scores')

    PlotData(X,imagepath,datafile)
    PlotScores(S,imagepath,scores)
    print("Successfully score and the score is:", S)

def partition(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]


def load_object(filename):
    with open(filename, 'rb') as output:
        trees = pickle.load(output)
    return trees
def sparkify_data(list, n):
    rdd = sc.parallelize(list)
    return rdd

def FormatData(X):
    datapoint = [float(x) for x in X.strip('()').split(',')]
    return datapoint

def PlotData(X,imagepath,datapath):
    TrainingData = np.genfromtxt(datapath+"/data.csv", delimiter=',')
    plt.figure(figsize=(7,7))
    plt.scatter(TrainingData[:,0],TrainingData[:,1],s=40,c=[.4,.4,.4])
    plt.scatter(X[0],X[1],s=100,c='r')
    plt.savefig(imagepath+'/data_point.png')

def PlotScores(S,imagepath,scores):
    f, axes = plt.subplots(1, 1, figsize=(7, 7), sharex=True)
    sb.distplot(scores, kde=True, color="b", ax=axes, axlabel='anomaly score')
    plt.axvline(x=S[0],color='r',linewidth=5)
    plt.savefig(imagepath+'/scores_point.png')

if __name__=="__main__":
    X         = sys.argv[1]
    datafile  = sys.argv[2]
    savepath  = sys.argv[3]
    imagepath = sys.argv[4]
    main(X, datafile, savepath, imagepath)
