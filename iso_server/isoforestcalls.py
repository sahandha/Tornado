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

def main(file):

    X = np.genfromtxt(file, delimiter=',')
    data_RDD = sc.parallelize(partition(X,int(len(X)/8)))
    Forest = data_RDD.map(lambda x: iso.iForest(x,ntrees=100, sample_size=256))
    S_t = Forest.map(lambda F: F.compute_paths(X))
    Scores  = S_t.reduce(lambda a,b: a+b)/8
    PlotData(X)
    PlotScores(Scores)
    PlotSortedData(X,Scores)


def partition(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]

def getSinglePointScore(pt):
    values = iso.compute_paths_single(pts)
    plt.hist(values,bins=np.linspace(0,1,20),normed=True,alpha=0.5)
    plt.savefig('/external/server/images/singlepoint_dist.png')
    print(values)

def FormatData(X):
    stringData = X.decode("utf-8")
    rows = stringData.rstrip('\n').split('\n')
    x = []
    y = []
    for row in rows:
        xy = row.split(',')
        x.append(float(xy[0]))
        y.append(float(xy[1]))
    xs = np.array(x)
    ys = np.array(y)
    Xdata = np.array([x,y]).T
    return Xdata

def PlotData(X):
    plt.figure(figsize=(7,7))
    plt.scatter(X[:,0],X[:,1],s=15,facecolor='k',edgecolor='k')
    plt.savefig('/external/server/images/data.png')

def PlotScores(Scores):
    f, axes = plt.subplots(1, 1, figsize=(7, 7), sharex=True)
    sb.distplot(Scores, kde=True, color="b", ax=axes, axlabel='anomaly score')
    plt.savefig('/external/server/images/scores.png')

def PlotSortedData(X,Scores):
    ss=np.argsort(Scores)
    x = X[:,0]
    y = X[:,1]
    plt.figure(figsize=(7,7))
    plt.scatter(x,y,s=15,c='b',edgecolor='b')
    plt.scatter(x[ss[-10:]],y[ss[-10:]],s=55,c='k')
    plt.scatter(x[ss[:10]],y[ss[:10]],s=55,c='r')
    plt.savefig('/external/server/images/sorteddata.png')

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def open_object(filename):
    with open(filename, 'rb') as input:
        forest = pickle.load(input)
    return forest

if __name__=="__main__":
    file = sys.argv[1]
    main(file)
