import Common_func
import os
import pandas
import stations.Station_ETL
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def scatter_3D(cluster_feature):
    fig = plt.figure()
    ax = Axes3D(fig)

    ax.scatter(cluster_feature[:, 0], cluster_feature[:, 1], cluster_feature[:, 2] % 100,
               edgecolor='k')

    ax.set_xlabel('grid_value')
    ax.set_ylabel('station_value')
    ax.set_zlabel('day')
    fig.show()


data_path = os.path.join(Common_func.UsePlatform(), 'grid_station_day.txt')
orig_data = pandas.read_csv(data_path, ',')
# print(len(orig_data))
grid_station_data = orig_data[(orig_data['gridval'] > 0) & (orig_data['stationval'] > 0)]
# print(len(grid_station_data), len(grid_station_data)/len(orig_data))
cluster_feature = grid_station_data[['gridval', 'stationval', 'date']].values

station_list = grid_station_data['stationID'].unique()

for stationid in station_list:

    lon, lat = stations.Station_ETL.get_lonlat_by_stationID(stationid)
    sum_days = len(orig_data[(orig_data['stationID'] == stationid)])
    val_days = len(grid_station_data[(grid_station_data['stationID'] == stationid)])
    cx_sum_days = 0
    cx_val_days = 0
    cx_start_fu = 0
    cx_end_fu = 0
    for year in range(2002, 2014):
        cx_start, cx_end = stations.Station_ETL.get_cx_by_stationID(stationid, year)
        cx_start_fu, month, day = Common_func.day_num_to_yyyymmdd(year, cx_start)
        cx_end_fu, month, day = Common_func.day_num_to_yyyymmdd(year, cx_end)
        cx_sum_days = cx_sum_days + len(orig_data[(orig_data['stationID'] == stationid) & (
                    orig_data['date'].astype(int) > int(cx_start_fu)) & (orig_data['date'].astype(int) < int(cx_end_fu))])
        cx_val_days = len(grid_station_data[
                              (orig_data['stationID'] == stationid) & (grid_station_data['date'] > int(cx_start_fu)) & (
                                          grid_station_data['date'] < int(cx_end_fu))])

    print(stationid, lon, lat, sum_days, val_days, "%.2f%%" % (val_days / sum_days * 100), cx_start_fu, cx_end_fu,
          cx_sum_days, cx_val_days,"%.2f%%" % (cx_val_days / cx_sum_days * 100))
