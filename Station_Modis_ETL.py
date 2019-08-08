import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import point_from_grid as pfg
import pandas as pd
import Modis_Fit, Modis_IO, Modis_Display,Modis_fill
import time
try:
    from osgeo import ogr
except:
    import ogr


# 因为Modis数据是按照一年的天数去存，而气象站点是按照日期去存
def get_station_value_by_num_day(root_path, year, daydir, StationID, T_tpye='HighestTemperature'):
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    month = f.month
    day = f.day
    data = pd.read_csv(root_path + '/meteodata.csv')
    station_value = data[(data['Year'] == int(year)) & (data['Months'] == int(month)) & (data['Days'] == int(day)) & (
            data['StationID'] == StationID)].head()
    try:
        station_high_value = (station_value[T_tpye].values[0].astype(int)) / 10
    except:
        station_high_value = -273.15
    # print(station_high_value)
    return fu, station_high_value



# band # 1是白天，2是晚上
# 读取一幅影像，找到上面所有的点
def get_grid_value_by_station_value(root_path, filename, year, day, band):
    print(root_path)
    lonlatlist = pd.read_csv( root_path + '/HHHstations.csv')
    for index, lonlatdata in lonlatlist.iterrows():
        try:
            lon = float(lonlatdata['Longitude'])
            lat = float(lonlatdata['Latitude'])
            StationID = lonlatdata['StationID']
            value = pfg.get_value_by_coordinates(filename, [lon, lat], band)
            tem_value = format(0.02 * value - 273.15, '.2f')
            date, station_high_value = get_station_value_by_num_day(root_path, year, day, StationID)
            row = str(StationID) + ',' + str(year) + ',' + str(date) + ',', str(tem_value), ',', str(station_high_value)
            Modis_IO.write_txt("grid_station_day.txt", row)
            print(row)
        except:
            print("No data")
            continue


def funcTest():
    root_path = 'G:\\mosicData\\'
    filename = 'G:\\mosicdata\\mosic2006\\168\\day\\result.tif'
    get_grid_value_by_station_value(filename,2006,168,1)

# funcTest()