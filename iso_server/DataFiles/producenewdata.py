import csv
import numpy as np




if __name__ == "__main__":

    mean = [10, 1]
    cov = [[1, 0], [0, 1]]  # diagonal covariance
    Nobjs = 4000
    x, y = np.random.multivariate_normal(mean, cov, Nobjs).T
    #Add manual outlier
    x[0]=3.3
    y[0]=3.3
    X=np.array([x,y]).T


    writer = csv.writer(open("data.csv", 'w'))
    for row in X:
        writer.writerow(row)
