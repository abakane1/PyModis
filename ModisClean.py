# coding:utf-8
from osgeo import gdal
import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import point_from_grid as pfg
import pandas as pd
import Modis_Fit, Modis_IO, Modis_Display
import time

try:
    from osgeo import ogr
except:
    import ogr


# todo 整体重构-功能模块太多了，要拆分


def get_station_value_by_num_day(year, daydir, StationID):
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    month = f.month
    day = f.day
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/stationdata.csv')
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


def get_grid_value_by_station_value(filename, year, daydir):
    band = 2
    lonlatlist = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/HSstation.csv')
    for index, lonlatdata in lonlatlist.iterrows():
        lon = float(lonlatdata['Longitude'])
        lat = float(lonlatdata['Latitude'])
        StationID = lonlatdata['StationID']
        value = pfg.get_value_by_coordinates(filename, [lon, lat], band)
        tem_value = 0.02 * value - 273.15
        daydir1, station_high_value = get_station_value_by_num_day(year, daydir, StationID)
        print(str(StationID) + ',' + str(year) + ',' + daydir1 + ',', tem_value, ',', station_high_value)


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
                        get_grid_value_by_station_value(filename, year, daydir)
                        #set_grid_value_by_linear(filename, year, daydir, 0.97116201, 4.834814562769491)


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



# 多年趋势补全
def multi_year_processing(root_path, begin_year, end_year):
    begin_day = 152
    end_day = 245
    day_band = 1  # 14:00
    nigh_tband = 2  # 02:00
    im_proj = None
    im_geotrans = None

    for day in range(begin_day, end_day):
        im_data_list = []
        file_path_list = []
        for year in range(begin_year, end_year + 1):
            file_path = root_path + 'mosic' + str(year) + '/' + str(day)
            filename = file_path + '/result_year_day.tif'

            if os.path.exists(filename):
                im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, day_band)
                im_data = im_data.flatten()
                im_data_list.append(im_data)
                file_path_list.append(file_path)

        # 填补 - 前后年平均
        im_data_list = np.transpose(im_data_list)
        col_num = im_data_list.shape[0]
        fill_num = 0
        for col in range(0, col_num):  # 逐行读取
        #num = np.isnan(im_data_list[col]).sum()
        #if num < im_data_list.shape[1]:
            row = im_data_list[col]
            for index in range(1, im_data_list.shape[1] - 2):
                if (row[index - 1] > 0) & (row[index + 1] > 0):
                    row[index] = (row[index - 1] + row[index + 1]) / 2
                    fill_num = fill_num + 1
                        # print(fill_num)
        # 存入
        im_data_list = np.transpose(im_data_list)
        for col in range(0, im_data_list.shape[0]):
            im_data = np.array(im_data_list[col]).reshape(1195, 2213)
            result_filename = file_path_list[col] + '/result_year_day.tif'
            Modis_IO.write_img(result_filename, im_proj, im_geotrans, im_data)
            print(result_filename + ' done')


# 多年趋势补全-同年
def multi_day_processing(root_path, begin_year, end_year):
    begin_day = 152
    end_day = 245
    day_band = 1  # 14:00
    nigh_tband = 2  # 02:00
    im_proj = None
    im_geotrans = None

    for year in range(begin_year, end_year+1):
        im_data_list = []
        file_path_list = []
        for day in range(begin_day, end_day):
            file_path = root_path + 'mosic' + str(year) + '/' + str(day)
            filename = file_path + '/result_year_day.tif'

            if os.path.exists(filename):
                im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, day_band)
                im_data = im_data.flatten()
                im_data_list.append(im_data)
                file_path_list.append(file_path)

        # 填补 - 前后日平均
        im_data_list = np.transpose(im_data_list)
        col_num = im_data_list.shape[0]
        fill_num = 0
        for col in range(0, col_num):  # 逐行读取
            #num = np.isnan(im_data_list[col]).sum()
            #if num < im_data_list.shape[1]:
            row = im_data_list[col]
            for index in range(1, im_data_list.shape[1] - 2):
                if (row[index - 1] > 0) & (row[index + 1] > 0):
                    row[index] = (row[index - 1] + row[index + 1]) / 2
                    fill_num = fill_num + 1
                        # print(fill_num)
        # 存入
        im_data_list = np.transpose(im_data_list)
        for col in range(0, im_data_list.shape[0]):
            im_data = np.array(im_data_list[col]).reshape(1195, 2213)
            result_filename = file_path_list[col] + '/result_year_day.tif'
            Modis_IO.write_img(result_filename, im_proj, im_geotrans, im_data)
            print(result_filename + ' done')


# 各种数据补全的思路
def pre_processing(root_path):
    begin_year = 2009
    end_year = 2009
    multi_year_processing(root_path,begin_year,end_year)
    multi_day_processing(root_path, begin_year, end_year)


if __name__ == "__main__":
    root_path = "/Volumes/Data/newmosicData/"
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
