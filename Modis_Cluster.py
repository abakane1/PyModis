# coding:utf-8
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D

data = pd.read_csv('G:\\staion-grid-withlanlon-data-.csv')
data = data[(data['grid_value'] < 500) & (data['station_value'] < 500) & (data['grid_value'] > 0) & (
            data['station_value'] > 0)]
cluster_feature = data[['grid_value', 'station_value', 'Elevation']].values

#print (cluster_feature)

kmeans = KMeans(n_clusters= 2, random_state= 0).fit(cluster_feature)
#print (kmeans.cluster_centers_)
fig = plt.figure()
ax = Axes3D(fig)

labels = kmeans.labels_

ax.scatter(cluster_feature[:, 0], cluster_feature[:, 1], cluster_feature[:, 2],
           c=labels.astype(np.float), edgecolor='k')

ax.set_xlabel('grid_value')
ax.set_ylabel('station_value')
ax.set_zlabel('Elevation')
fig.show()