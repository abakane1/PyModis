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


# todo 整体重构-功能模块太多了，要拆分
# 读图像文件
def read_img(filename, band):
    """
    读取tif，返回数组，仿射矩阵，投影
    :param filename: 文件名称
    :param band: 获取的波段
    :return: im_data:数组
    :return: im_geotrans:仿射变换参数
    :return: im_proj:投影
    """
    dataset = gdal.Open(filename)  # 打开文件
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数

    im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
    im_proj = dataset.GetProjection()  # 地图投影信息

    # im_data = dataset.GetRasterBand(5)
    im_data = dataset.GetRasterBand(band)
    im_data = im_data.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵

    return im_data, im_geotrans, im_proj
    del dataset

    # 写文件，以写成tif为例


def write_img(filename, im_proj, im_geotrans, b):
    """
    存计算结果
    :param filename:
    :param im_proj:
    :param im_geotrans:
    :param b:
    :return:
    """
    # gdal数据类型包括
    # gdal.GDT_Byte,
    # gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
    # gdal.GDT_Float32, gdal.GDT_Float64

    # 判断栅格数据的数据类型
    if 'int8' in b.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in b.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    # 判读数组维数
    if len(b.shape) == 3:
        im_bands, im_height, im_width = b.shape
    else:
        im_bands, (im_height, im_width) = 1, b.shape

    # 创建文件
    driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    dataset.SetProjection(im_proj)  # 写入投影

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(b)  # 写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(b[i])

    del dataset


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
    driver = ogr.GetDriverByName('ESRI Shapefile')
    county_shp = '/Volumes/Data/county/黄淮海县域.shp'
    dataSource = driver.Open(county_shp, 0)
    if dataSource is None:
        print('could not open')
    layer = dataSource.GetLayer(0)
    n = layer.GetFeatureCount()
    print(n)
    # plt.imshow(amount_data)
    # plt.imshow(county_shp)
    # plt.colorbar()
    # plt.show()
    dataSource.Destroy()


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
        station_high_value = (station_value['HighestTemperature'].values[0].astype(int)) / 10
    except:
        station_high_value = -273.15
    # print(station_high_value)
    return fu, station_high_value


def Statics(amount_data, year):
    amountData = amount_data.flatten()  # 二维转一维
    print(year + 'mean:', np.nanmean(amount_data))
    print(year + 'median', np.nanmedian(amount_data))
    print(year + 'std', np.nanstd(amount_data))
    # print(np.histogram(amountData, bins=62, range=[0, 60],normed= False))


def staion_value_and_grid_value(filename, year, daydir):
    lonlatlist = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/HSstation.csv')
    for index, lonlatdata in lonlatlist.iterrows():
        lon = float(lonlatdata['Longitude'])
        lat = float(lonlatdata['Latitude'])
        StationID = lonlatdata['StationID']
        value = pfg.get_value_by_coordinates(filename, [lon, lat])
        tem_value = 0.02 * value - 273.15
        daydir1, station_high_value = get_station_value_by_num_day(year, daydir, StationID)
        print(str(StationID) + ',' + str(year) + ',' + daydir1 + ',', tem_value, ',', station_high_value)


def every_staion(root_path, year):
    data_path = root_path + 'mosic' + year + '/'
    for roots, dir, file in os.walk(data_path):
        for daydir in dir:
            rootPaths = data_path + daydir
            for root, dirs, files in os.walk(rootPaths):
                for LST in files:
                    if LST == "result_multi_year_day.tif":
                        filename = rootPaths + "/" + LST
                        # staion_value_and_grid_value(filename, year, daydir)
                        set_grid_value_by_linear(filename, year, daydir, 0.97116201, 4.834814562769491)


def set_grid_value_by_linear(filename, year, daydir, a, b):
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/staion-grid-withlanlon.csv')
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(daydir) - 1)
    fu = f.strftime('%Y%m%d')
    date = str(fu)
    data_station_date = data[(data['date'] == int(date)) & (data['grid_value'] <0)&(data['station_value']>0)]
    data_station_date['grid_value'] = (a * data_station_date['station_value']+b+273.15)/0.02
    im_data, im_geotrans, im_proj = pfg.set_value_by_coordinates(filename, data_station_date)
    write_img(filename, im_proj, im_geotrans, im_data)


# 计算每个相元的数量
def EveryPoint(root_path, year):
    # todo 这部分是可以复用的，可以重构
    # amount_data = np.zeros((2400, 2400))
    data_path = root_path + 'mosic' + year + '/'
    amount_data = np.zeros((1195, 2213))
    result_filename = 'result_multi_year_day.tif'
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

                        im_data, im_geotrans, im_proj = read_img(filename, day_band)
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
    write_img(root_path + 'result/' + year + result_filename, im_proj, im_geotrans, amount_data)
    print('days:', pic_num)

    # DisAsHist(amount_data)
    # Statics(amount_data)
    # DisAsImage(amount_data)


def results(root_path, year):
    day_band = 1
    orig_file = root_path + 'orig/result' + year + '.tif'
    clean_file = root_path + 'result/' + year + 'result_multi_year_day.tif'
    orig_data, im_geotrans, im_proj = read_img(orig_file, day_band)
    clean_data, im_geotrans, im_proj = read_img(clean_file, day_band)
    clean_data = clean_data.flatten()
    orig_data = orig_data.flatten()
    plt.hist(orig_data, bins=30, range=(-1, 90), normed=False, edgecolor="black")
    plt.hist(clean_data, bins=30, range=(-1, 90), normed=False, edgecolor="black", alpha=0.5)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.xlabel("有数据天数")
    plt.ylabel("像元数")
    plt.title(year)
    plt.show()
    # DisAsHist(orig_data, year)
    # DisAsImage(amount_data, year, im_geotrans, im_proj)


def Fit():
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/station-grid copy.csv')
    data = data[(data['grid_value'] <500) & (data['station_value'] < 500)&(data['grid_value'] >-300) &(data['station_value'] >-300)  ]
    # 用1次多项式拟合
    # x = data['grid_value'].values
    # y = data['station_value'].values

    # fit_by_staion(data)
    #fit_by_year(data)
    DisAsScatter(data)


def fit_by_staion(data):
    stationlist = data['stationID'].unique()
    for station in stationlist:
        station_value = data[data['stationID'] == station]
        y = station_value['grid_value'].values
        x = station_value['station_value'].values
        # print(station)
        linear_fit(x, y)


def fit_by_year(data):
    for year in range(2003, 2015):
        station_value = data[data['year'] == year]
        y = station_value['grid_value'].values
        x = station_value['station_value'].values
        print(year)
        linear_fit(x, y)


# 一元线性回归-numpy
def linear_fit(x, y):
    f1 = np.polyfit(x, y, 1)
    p1 = np.poly1d(f1)
    # fit values, and mean
    yhat = p1(x)  # or [p(z) for z in x]
    ybar = np.sum(y) / len(y)  # or sum(y)/len(y)
    ssreg = np.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
    print(ssreg / sstot)
    # print('a:', f1[0], 'b:', f1[1], 'r2:', ssreg / sstot)


# 多元线性回归- sklearn
def multi_linear_fit(year):
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/staion-grid-withlanlon.csv')
    data = data[(data['grid_value'] > 0) & (data['station_value'] > 0) & (data['stationid'] == 53898)]
    X = np.array(data.loc[:, 'station_value']).reshape(-1, 1)
    y = data.loc[:, 'grid_value']
    # y = pd.factorize(data.loc[:,'grid_value'].values)[0].reshape(-1, 1)
    print(year)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)
    print('X_train.shape={}\n y_train.shape ={}\n X_test.shape={}\n,  y_test.shape={}'.format(X_train.shape,
                                                                                              y_train.shape,
                                                                                              X_test.shape,
                                                                                              y_test.shape))
    linreg = LinearRegression()
    model = linreg.fit(X, y)
    # print(model)
    # 训练后模型截距
    print(linreg.intercept_)
    # 训练后模型权重（特征个数无变化）
    print(linreg.coef_)
    feature_cols = ['station_value']
    B = list(zip(feature_cols, linreg.coef_))
    # print(B)

    # 预测
    y_pred = linreg.predict(X_test)
    # print(y_pred)
    # calculate RMSE by hand
    print("RMSE", metrics.mean_absolute_error(y_test, y_pred))
    # print(metrics.mean_squared_error(y_test, y_pred))
    print("R2", metrics.r2_score(y_test, y_pred))
    # 做ROC曲线
    plt.figure()
    plt.plot(range(len(y_pred)), y_pred, 'b', label="predict")
    plt.plot(range(len(y_pred)), y_test, 'r', label="test", alpha=0.5)
    # plt.scatter(y_pred, y_test)
    plt.legend(loc="upper right")  # 显示图中的标签
    plt.xlabel("the number of sales")
    plt.ylabel('value of sales')
    plt.title(str(53898))
    plt.show()


def DisAsScatter(data):
    x = data['grid_value']
    y = data['station_value']
    plt.xlabel("grid_value")
    plt.ylabel("station_value")
    plt.scatter(x, y)
    plt.show()


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
            filename = file_path + '/result.tif'

            if os.path.exists(filename):
                im_data, im_geotrans, im_proj = read_img(filename, day_band)
                im_data = im_data.flatten()
                im_data_list.append(im_data)
                file_path_list.append(file_path)

        # 填补 - 前后年平均
        im_data_list = np.transpose(im_data_list)
        col_num = im_data_list.shape[0]
        fill_num = 0
        for col in range(0, col_num):  # 逐行读取
            num = np.isnan(im_data_list[col]).sum()
            if num < im_data_list.shape[1]:
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
            result_filename = file_path_list[col] + '/result_multi_year.tif'
            write_img(result_filename, im_proj, im_geotrans, im_data)
            print(result_filename + ' done')


# 多年趋势补全-同年
def multi_day_processing(root_path, begin_year, end_year):
    begin_day = 152
    end_day = 245
    day_band = 1  # 14:00
    nigh_tband = 2  # 02:00
    im_proj = None
    im_geotrans = None

    for year in range(begin_year, end_year):
        im_data_list = []
        file_path_list = []
        for day in range(begin_day, end_day):
            file_path = root_path + 'mosic' + str(year) + '/' + str(day)
            filename = file_path + '/result_multi_year_night.tif'

            if os.path.exists(filename):
                im_data, im_geotrans, im_proj = read_img(filename, day_band)
                im_data = im_data.flatten()
                im_data_list.append(im_data)
                file_path_list.append(file_path)

        # 填补 - 前后日平均
        im_data_list = np.transpose(im_data_list)
        col_num = im_data_list.shape[0]
        fill_num = 0
        for col in range(0, col_num):  # 逐行读取
            num = np.isnan(im_data_list[col]).sum()
            if num < im_data_list.shape[1]:
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
            result_filename = file_path_list[col] + '/result_multi_year_day_night.tif'
            write_img(result_filename, im_proj, im_geotrans, im_data)
            print(result_filename + ' done')


# 各种数据补全的思路
def pre_processing(root_path):
    begin_year = 2003
    end_year = 2015
    multi_day_processing(root_path, begin_year, end_year)


if __name__ == "__main__":
    # Macos
    # root_path = "/Volumes/Data/newmosicData/"
    # Windows
    root_path = "E:\\newmosicData"
    # starttime = datetime.datetime.now()

    # 对原始数据进行统计分析部分
    # todo 需要重构
    # begin_year = 2003
    # end_year = 2014
    # for i in range(begin_year, end_year):
    #    year = str(i)

    # 计算函数
    # year = str('2014')
    # EveryPoint(root_path, year)
    # 统计做图
    # results(root_path, year)

    # 气象点和格网点的关系方法
    #every_staion(root_path, '2009')

    # 计算时间
    # endtime = datetime.datetime.now()
    # print((endtime - starttime).seconds)

    # 拟合
    # Fit()

    # begin_year = 2003
    # end_year = 2015
    # for i in range(begin_year, end_year):
    #    year = i
    # multi_linear_fit(2009)

    # pre_processing(root_path)