# coding:utf-8
from osgeo import gdal
import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import point_from_grid as pfg
import pandas as pd
import Modis_Fit, Modis_IO, Modis_Display, Modis_fill,Station_Modis_ETL, Common_func
import time

try:
    from osgeo import ogr
except:
    import ogr




def Statics(amount_data, year):
    amount_data = amount_data.flatten()  # 二维转一维
    print(year + 'mean:', np.nanmean(amount_data))
    print(year + 'median', np.nanmedian(amount_data))
    print(year + 'std', np.nanstd(amount_data))
    # print(np.histogram(amountData, bins=62, range=[0, 60],normed= False))


def EveryPoint(root_path, year, time='day', orig_file='result.tif'):
    """
    按年遍历所有年份的数据
    :param root_path:文件路径
    :param year: 年份
    :return:
    """
    # amount_data = np.zeros((2400, 2400))
    data_path = os.path.join(root_path, 'mosic'+year)
    amount_data = np.zeros((1221, 2224))
    band = 1
    # amount_data = np.where(amount_data == 0, np.nan, 0)
    pic_num = 0
    im_proj = ''
    im_geotrans = ''

    for roots, dir, file in os.walk(data_path):
        #print (dir)
        for daydir in dir:
            rootPaths = os.path.join(data_path, daydir, time)
            #print(root_path)
            for root, dirs, files in os.walk(rootPaths):
                if orig_file in files:
                    filename = os.path.join(rootPaths,orig_file)
                    print(filename)

                    Station_Modis_ETL.get_grid_value_by_station_value(root_path, filename,year,daydir,band=1)


                    # im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, band)
                    # im_data = np.where(im_data > 0, 1, im_data)
                    # im_data = np.where(im_data < 0, -1, im_data)
                    # print(np.sum(im_data))
                    # amount_data = np.ma.masked_array(im_data,np.logical_not(im_data))
                    print(year+":"+ daydir+":"+filename)
                    #amount_data = amount_data + im_data
                    pic_num = pic_num + 1

    # amount_data = np.where(amount_data > 0, amount_data.astype(int), 0)
    amount_data = np.where(amount_data >= 0, amount_data.astype(int), np.nan)
    # 保存计算结果，不需要每次都计算
    # Modis_IO.write_img(root_path + 'result/3' + year + result_filename, im_proj, im_geotrans, amount_data)
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
    # Modis_Display.DisAsImage(clean_data, year, im_geotrans, im_proj)
    # Modis_Display.DisAsImage(clean_data1, year, im_geotrans, im_proj)
    clean_data = clean_data.flatten()
    clean_data1 = clean_data1.flatten()
    orig_data = orig_data.flatten()
    # plt.hist(orig_data, bins=30, range=(1, 90), color='red', normed=False, edgecolor="black")
    plt.hist(clean_data, bins=30, range=(1, 90), color='green', normed=False, edgecolor="black", alpha=0.5)
    # plt.hist(clean_data1, bins=30, range=(1, 90), color='blue', normed=False, edgecolor="black", alpha=0.1)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.xlabel("有数据天数")
    plt.ylabel("像元数")
    plt.title(year)
    plt.show()
    # DisAsHist(orig_data, year)


def FuncTest():
    root_path = Common_func.UsePlatform()
    starttime = datetime.datetime.now()
    begin_year = 2018
    end_year = 2019
    for i in range(begin_year, end_year):
        year = str(i)
        EveryPoint(root_path, year,time='day')
    # 计算函数
    # year = str('2005')
    # 统计做图
    # results(root_path, year)

    # 气象点和格网点的关系方法
    #    every_station(root_path, year)

    # 计算时间
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)

    # 拟合
    # Modis_Fit.Fit()

    # begin_year = 2003
    # end_year = 2015
    # for i in range(begin_year, end_year):
    #    year = i
    # multi_linear_fit(2009)

    # pre_processing(root_path)

FuncTest()