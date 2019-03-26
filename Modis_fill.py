# coding:utf-8
from osgeo import gdal
import os
import numpy as np
import datetime
import Modis_IO
import time

try:
    from osgeo import ogr
except:
    import ogr


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
            # num = np.isnan(im_data_list[col]).sum()
            # if num < im_data_list.shape[1]:
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

    for year in range(begin_year, end_year + 1):
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
            # num = np.isnan(im_data_list[col]).sum()
            # if num < im_data_list.shape[1]:
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
    multi_year_processing(root_path, begin_year, end_year)
    multi_day_processing(root_path, begin_year, end_year)
