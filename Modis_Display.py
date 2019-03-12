# coding:utf-8
from osgeo import gdal
import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import point_from_grid as pfg
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import time
try:
    from osgeo import ogr
except:
    import ogr

# grams hist
def DisAsHist(amountData, year):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    amountData = amountData.flatten()
    plt.hist(amountData, bins=60, range=(-1, 60), normed=False, edgecolor="black")
    plt.xlabel("有数据天数")
    plt.ylabel("像元数")
    # todo 统一y轴的显示范围。x轴已经统一
    # plt.ylim(0,7000)
    plt.title(year)
    plt.show()


def DisAsImage(amount_data, year, im_geotrans, im_proj):
    # todo 增加叠加矢量，转投影
    #driver = ogr.GetDriverByName('ESRI Shapefile')
    #county_shp = '/Volumes/Data/county/黄淮海县域.shp'
    #dataSource = driver.Open(county_shp, 0)
    #if dataSource is None:
    #    print('could not open')
    #layer = dataSource.GetLayer(0)
    #n = layer.GetFeatureCount()
    #print(n)
    plt.imshow(amount_data)
    #plt.imshow(county_shp)
    plt.colorbar()
    plt.show()
    #dataSource.Destroy()