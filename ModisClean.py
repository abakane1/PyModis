# coding:utf-8
from osgeo import gdal
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


# todo 整体重构-功能模块太多了，要拆分

# 因为Modis数据是按照一年的天数去存，而气象站点是按照日期去存
def get_station_value_by_num_day(year, daydir, StationID):
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    month = f.month
    day = f.day
    data = pd.read_csv('stationdata.csv')
    station_value = data[(data['Year'] == int(year)) & (data['Months'] == int(month)) & (data['Days'] == int(day)) & (
            data['StationID'] == StationID)].head()
    try:
        station_high_value = (station_value['LowestTemperature'].values[0].astype(int)) / 10
    except:
        station_high_value = -273.15
    # print(station_high_value)
    return fu, station_high_value


def Statics(amount_data, year):
    amount_data = amount_data.flatten()  # 二维转一维
    print(year + 'mean:', np.nanmean(amount_data))
    print(year + 'median', np.nanmedian(amount_data))
    print(year + 'std', np.nanstd(amount_data))
    # print(np.histogram(amountData, bins=62, range=[0, 60],normed= False))

# band # 1是白天，2是晚上
# 读取一幅影像，找到上面所有的点
def get_grid_value_by_station_value(filename, year, day, band):

    lonlatlist = pd.read_csv('HSstation.csv')
    for index, lonlatdata in lonlatlist.iterrows():
        lon = float(lonlatdata['Longitude'])
        lat = float(lonlatdata['Latitude'])
        StationID = lonlatdata['StationID']
        value = pfg.get_value_by_coordinates(filename, [lon, lat], band)
        tem_value = 0.02 * value - 273.15
        date, station_high_value = get_station_value_by_num_day(year, day, StationID)
        row = str(StationID) + ',' + str(year) + ',' + str(date) + ',', str(tem_value), ',', str(station_high_value)
        Modis_IO.write_txt("result.txt", row)
        print(row)

# 读取每一景的信息
def every_station(root_path, year):
    result_filename = 'result.tif'
    data_path = root_path + 'mosic' + year + '/'
    for roots, dir, file in os.walk(data_path):
        for daydir in dir:
            rootPaths = data_path + daydir
            for root, dirs, files in os.walk(rootPaths):
                for LST in files:
                    if LST == result_filename:
                        filename = rootPaths + "/" + LST
                        get_grid_value_by_station_value(filename, year, daydir, band=2) # 存储的dir就是天数
                        #set_grid_value_by_linear(filename, year, daydir, 0.97116201, 4.834814562769491)


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


# 计算每个相元的数量
def EveryPoint(root_path, year):
    # todo 这部分是可以复用的，可以重构
    # amount_data = np.zeros((2400, 2400))
    data_path = root_path + 'mosic' + year + '/'
    amount_data = np.zeros((1195, 2213))
    result_filename = 'result_year_day.tif'
    day_band = 1  # 14:00
    nigh_tband = 2  # 02:00
    # amount_data = np.where(amount_data == 0, np.nan, 0)
    pic_num = 0
    im_proj = ''
    im_geotrans = ''
    for roots, dir, file in os.walk(data_path):
        for daydir in dir:
            rootPaths = data_path + daydir
            for root, dirs, files in os.walk(rootPaths):
                for LST in files:
                    if LST == result_filename:
                        filename = rootPaths + "/" + LST

                        im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, day_band)
                        # if pic_num == 0:
                        #    im_data_grid = np.where(im_data > 0, 1, im_data)
                        #    amount_data = amount_data + im_data_grid
                        im_data = np.where(im_data > 0, 1, im_data)
                        # im_data = np.where(im_data < 0, -1, im_data)
                        # print(np.sum(im_data))
                        # amount_data = np.ma.masked_array(im_data,np.logical_not(im_data))
                        print(daydir)
                        amount_data = amount_data + im_data
                        pic_num = pic_num + 1

    # amount_data = np.where(amount_data > 0, amount_data.astype(int), 0)
    amount_data = np.where(amount_data >= 0, amount_data.astype(int), np.nan)
    # 保存计算结果，不需要每次都计算
    Modis_IO.write_img(root_path + 'result/3' + year + result_filename, im_proj, im_geotrans, amount_data)
    print('days:', pic_num)

    # DisAsHist(amount_data)
    # Statics(amount_data)
    # DisAsImage(amount_data)


def results(root_path, year):
    day_band = 1
    orig_file = root_path + 'orig/result' + year + '.tif'
    clean_file = root_path + 'result/3' + year + 'result_year_day.tif'
    clean_file1 = root_path + 'result/2' + year + 'result_year_day.tif'
    orig_data, im_geotrans, im_proj = Modis_IO.read_img(orig_file, day_band)
    clean_data, im_geotrans, im_proj = Modis_IO.read_img(clean_file, day_band)
    clean_data1, im_geotrans, im_proj = Modis_IO.read_img(clean_file1, day_band)
    #Modis_Display.DisAsImage(clean_data, year, im_geotrans, im_proj)
    #Modis_Display.DisAsImage(clean_data1, year, im_geotrans, im_proj)
    clean_data = clean_data.flatten()
    clean_data1 = clean_data1.flatten()
    orig_data = orig_data.flatten()
    #plt.hist(orig_data, bins=30, range=(1, 90), color='red', normed=False, edgecolor="black")
    plt.hist(clean_data, bins=30, range=(1, 90), color='green', normed=False, edgecolor="black", alpha=0.5)
    #plt.hist(clean_data1, bins=30, range=(1, 90), color='blue', normed=False, edgecolor="black", alpha=0.1)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.xlabel("有数据天数")
    plt.ylabel("像元数")
    plt.title(year)
    plt.show()
    # DisAsHist(orig_data, year)






if __name__ == "__main__":
    # MacOS
    # root_path = "/Volumes/Data/newmosicData/"
    # Windows
    root_path = "E:\\newmosicData\\"
    # starttime = datetime.datetime.now()

    # 对原始数据进行统计分析部分
    # todo 需要重构
    begin_year = 2003
    end_year = 2014
    for i in range(begin_year, end_year):
        year = str(i)

    # 计算函数
    #year = str('2009')
    #EveryPoint(root_path, year)
    # 统计做图
    #results(root_path, year)

    # 气象点和格网点的关系方法
        every_station(root_path, year)

    # 计算时间
    # endtime = datetime.datetime.now()
    # print((endtime - starttime).seconds)

    # 拟合
    # Modis_Fit.Fit()

    # begin_year = 2003
    # end_year = 2015
    # for i in range(begin_year, end_year):
    #    year = i
    # multi_linear_fit(2009)

    # pre_processing(root_path)
