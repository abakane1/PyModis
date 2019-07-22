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
def get_station_value_by_num_day(year, daydir, StationID, T_tpye='HighestTemperature'):
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    month = f.month
    day = f.day
    data = pd.read_csv('G:\\mosicData\\stationdata.csv')
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
def get_grid_value_by_station_value(filename, year, day, band):

    lonlatlist = pd.read_csv('G:\\mosicData\\HSstation.csv')
    for index, lonlatdata in lonlatlist.iterrows():
        lon = float(lonlatdata['Longitude'])
        lat = float(lonlatdata['Latitude'])
        StationID = lonlatdata['StationID']
        value = pfg.get_value_by_coordinates(filename, [lon, lat], band)
        tem_value = 0.02 * value - 273.15
        date, station_high_value = get_station_value_by_num_day(year, day, StationID)
        row = str(StationID) + ',' + str(year) + ',' + str(date) + ',', str(tem_value), ',', str(station_high_value)
        Modis_IO.write_txt("grid_station_day.txt", row)
        print(row)


# todo 20190321 确认bug 修改
#  目前这个函数的逻辑是错误的，正确的业务应该应该
#  1：根据每一个grid value的值生成一个新的station value
#  2：最后生成一幅新的tif为完整的气温数据
def set_grid_value_by_linear(filename, year, daydir, a, b):
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/staion-grid-withlanlon.csv')
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    date = str(fu)
    data_station_date = data[(data['date'] == int(date)) & (data['grid_value'] < 0) & (data['station_value'] > 0)]
    data_station_date['grid_value'] = (a * data_station_date['station_value'] + b + 273.15) / 0.02
    im_data, im_geotrans, im_proj = pfg.set_value_by_coordinates(filename, data_station_date)
    Modis_IO.write_img(filename, im_proj, im_geotrans, im_data)




def funcTest():
    root_path = 'G:\\mosicData\\'
    filename = 'G:\\mosicdata\\mosic2006\\168\\day\\result.tif'
    get_grid_value_by_station_value(filename,2006,168,1)

funcTest()