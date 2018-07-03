#---------------------References---------------------------------------
# 1.https://matplotlib.org/2.1.1/gallery/shapes_and_collections/scatter.html
# 2.https://pythonspot.com/matplotlib-scatterplot/
# 3.https://jakevdp.github.io/PythonDataScienceHandbook/04.02-simple-scatter-plots.html
# 4.http://blog.mpacula.com/2011/04/27/k-means-clustering-example-python/
# 5.http://www.awesomestats.in/python-cluster-validation/
# 6.https://community.esri.com/thread/158038
#----------------------------------------------------------------------------
#Importing the necessary packages to run the program
import matplotlib
matplotlib.use('Agg')
import sqlite3 as sql
import os
from collections import Counter
import numpy as math
import pandas as pd
from matplotlib import pylab as plt
from flask import Flask, render_template, request
from numpy import array
from scipy.cluster.vq import *

#Connect to the Database and read data from the CSV file and import it to DB using Pandas Package
app = Flask(__name__,template_folder="static")
conn = sql.connect('Assign4Sql.db')
csvf = pd.read_csv("minnow.csv",encoding = "ISO-8859-1")
csvf.to_sql('minnow', conn, if_exists='replace', index=False)
conn.commit()
conn.close()


#Retruns to the homepage#
@app.route('/')
def index():
  return render_template('index.html')


#Using Kmeans Algorithm, the clusters with centroids and Number of points are calculated by giving two column names from the Db table as input#

Coordlist = []
@app.route('/kmeans', methods=['POST'])
def kmeans():
    maxPts = []
    ptsdist = []
    messageTight = []
    Coordlist = []
    datav1 = request.form['data1']
    datav2 = request.form['data2']
    clustersValue = request.form['clustersValue']
    NoOfclusters = int(clustersValue)
    con = sql.connect("Assign4Sql.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM minnow')
    rows = cur.fetchall()
    for row in rows:
        pair = []
        xtemp=row[str(datav1)]
        ytemp=row[str(datav2)]
        if xtemp is not None:
            x = float(xtemp)
        if ytemp is not None:
            y = float(ytemp)


        pair.append(x)
        pair.append(y)
        Coordlist.append(pair)


    clusterdist = []
    data = array(Coordlist)
    centroid, pts = kmeans2(data, NoOfclusters) #Kmeans Algorithm calculates the centroid and points and forms clusters with the provided Data
    distanceCluster = []

    #The distance between the centroids of each clusters is calculated with Distance Formula
    for i in range(len(centroid)):
            x1 = centroid[i][0]
            y1 = centroid[i][1]
            x1 = float("{0:.3f}".format(x1))
            y1 = float("{0:.3f}".format(y1))


            for j in range(i+1,len(centroid)):
                dc = {}
                x2 = centroid[j][0]
                y2 = centroid[j][1]
                x2 = float("{0:.3f}".format(x2))
                y2 = float("{0:.3f}".format(y2))
                dist = math.sqrt(((x1-x2)*(x1-x2)) + ((y1-y2)*(y1-y2)))
                dc['dist'] = "Distance between centroid of cluster " + str(i+1) + " and centroid of cluster " + str(j+1) + " is: " + str(dist)
                distanceCluster.append(dc)



    # the number of points in a clusters is returned
    points_in_cluster = []
    minValue = []
    count = Counter(pts)
    for i in range(0, NoOfclusters):
        points_in_cluster.append(count[i])

    # The positions of centroid is returned
    centroids_in_cluster = []
    centroid_message = []
    count = Counter(pts)
    for i in range(0, NoOfclusters):
        centroids_in_cluster.append(centroid[i][0])
        centroids_in_cluster.append(centroid[i][1])
        Cmsg = "Centroid points are " + str(centroids_in_cluster[0]) + " and  " + str(centroids_in_cluster[1]) + ""
        centroid_message.append(Cmsg)
        centroids_in_cluster = []

   #The nearest centroid for each centroid is calculated and stored in an array
        for i in range(len(centroid)):
            x1 = centroid[i][0]
            y1 = centroid[i][1]

            x1 = float("{0:.3f}".format(x1))
            y1 = float("{0:.3f}".format(y1))
            for j in range(0, len(centroid)):
                if (i != j):
                    x2 = centroid[j][0]
                    y2 = centroid[j][1]
                    x2 = float("{0:.3f}".format(x2))
                    y2 = float("{0:.3f}".format(y2))
                    dist = math.sqrt(((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))
                    clusterdist.append(dist)

            minValue.append(min(clusterdist))
            clusterdist = []
    #The maximum Distance of point in a clusters is calculated and stored

        for i in range(len(centroid)):
                x1 = centroid[i][0]
                y1 = centroid[i][1]
                x1 = float("{0:.3f}".format(x1))
                y1 = float("{0:.3f}".format(y1))
                count = Counter(pts)
                for j in range(count[i]):
                    x2 = pts[j]
                    y2 = pts[j+1]
                    j=j+2
                    x2 = float("{0:.3f}".format(x2))
                    y2 = float("{0:.3f}".format(y2))
                    distance = math.sqrt(((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))
                    ptsdist.append(distance)
                maxPts.append(max(ptsdist,default=0))
                ptsdist=[]

        #The Cluster is tightly packed or loosely packed are verfied and returned to the webpage
        for i in range(len(centroid)):
            if(minValue[i]>maxPts[i]):
                msg="Cluster "+str(i+1)+" is tightly packed"
                messageTight.append(msg)
            elif(minValue[i]<maxPts[i]):
                msg="Cluster "+str(i+1)+" is loosely packed"
                messageTight.append(msg)

    #The centroids and points in clusters are plotted in a scatter plot and displayed
    clr = math.random.rand(50)
    colors = ([(clr)[i] for i in pts])
    plt.scatter(data[:, 0], data[:, 1], marker='o', s=10, c=colors)
    plt.scatter(centroid[:, 0], centroid[:, 1], s=100, marker='x', linewidths=3, c='black')
    plt.savefig("static/clustersImage.png")
    plt.gcf().clear()
    plt.clf()
    plt.cla()
    plt.close()


    return render_template('index.html',distanceCluster=distanceCluster,pts=points_in_cluster,mess=messageTight,centroidVal=centroid_message)


#Returns the page where the scatter plot is displayed
@app.route('/TightCluster', methods=['POST'])
def TightCluster():

    return render_template('Display.html')

# PORT = int(os.getenv('PORT','5000'))
# if __name__ == '__main__':
#     app.run(debug=True)

# Copy this when deploying it to Cloud
PORT = int(os.getenv('PORT','8000'))
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=PORT)