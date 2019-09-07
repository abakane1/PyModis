import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Common_func

root_path = Common_func.UsePlatform()

def get_lonlat_by_stationID(stationID):
    station_list = pd.read_csv(os.path.join(root_path, 'HHHstations.csv'))
    lon = station_list[(station_list['StationID'] == stationID)]['Longitude'].values[0]
    lat = station_list[(station_list['StationID'] == stationID)]['Latitude'].values[0]
    return lon,lat

def get_station_name_by_stationID(stationID):
    station_list = pd.read_csv(os.path.join(root_path, 'HHHstations.csv'))
    station_name = station_list[(station_list['StationID'] == stationID)]['StationName'].values[0]
    return station_name

def get_cx_by_stationID(stationID,year):
    cx_data = pd.read_csv(Common_func.cx," ")
    cx_start = cx_data[(cx_data['stationID'] == stationID) & (cx_data['year'] == year)]['cx_start'].values[0]
    cx_end = cx_data[(cx_data['stationID'] == stationID) & (cx_data['year'] == year)]['cx_end'].values[0]
    return cx_start,cx_end

def station_year():
    '''
    查看气象站点有数据的年份
    :return:
    '''
    station_list = pd.read_csv(os.path.join(root_path, 'HHHstations.csv'))
    # print(os.path.join(root_path,'HHHstations.csv'))

    data = pd.read_csv(os.path.join(root_path, 'meteodata.csv'))

    x = []
    y = []
    for index, station_data in station_list.iterrows():
        station_ID = station_data['StationID']
        station_name = station_data['StationName']
        year_list = data[data['StationID'] == station_ID]['Year'].unique()
        # print(station_ID,year_list)
        print(station_ID, station_name, station_data['Latitude'], station_data['Longitude'], len(year_list))
        x.append(station_ID)
        y.append(len(year_list))
    # for year in year_list:
    #    x.append(station_name)
    #    y.append(year)
    # 年际分布
    # print(x,y)
    # plt.scatter(x,y)
    # plt.show()

def aro_station_year():
    pass
