# coding:utf-8
import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import Modis_IO, Common_func
import pandas_profiling
import pandas as pd
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


def feature_cluster(dataset):
    '''
    dataset 一行就是一景影像，一列就是一个时间序列
    :param dataset:
    :return:
    '''
    im_data_list_mean = np.nanmean(dataset)
    im_data_list_std = np.nanstd(dataset)
    low_2s = im_data_list_mean - 2 * im_data_list_std
    low_s = im_data_list_mean - im_data_list_std
    high_s = im_data_list_mean + im_data_list_std
    high_2s = im_data_list_mean + 2 * im_data_list_std
    dataset = np.where(dataset < (low_2s), -2, dataset)
    dataset = np.where((low_2s <= dataset) & (dataset < low_s), -1, dataset)
    dataset = np.where((low_s <= dataset) & (dataset < high_s), 0, dataset)
    dataset = np.where((high_s <= dataset) & (dataset < high_2s), 1, dataset)
    dataset = np.where(dataset >= high_2s, 2, dataset)
    return dataset


def EveryPoint(root_path, year, time='day', orig_file='RHF.tif'):
    """
    按年遍历所有年份的数据
    :param root_path:文件路径
    :param year: 年份
    :return:
    """
    # amount_data = np.zeros((2400, 2400))
    data_path = os.path.join(root_path, 'mosic' + year)
    amount_data = np.zeros((1221, 2224))
    band = 1
    # amount_data = np.where(amount_data == 0, np.nan, 0)
    pic_num = 0
    im_proj = ''
    im_geotrans = ''

    for roots, dir, file in os.walk(data_path):
        # print (dir)
        for daydir in dir:
            rootPaths = os.path.join(data_path, daydir, time)
            # print(root_path)
            for root, dirs, files in os.walk(rootPaths):
                if orig_file in files:
                    filename = os.path.join(rootPaths, orig_file)
                    print(filename)

                    # Station_Modis_ETL.get_grid_value_by_station_value(root_path, filename,year,daydir,band=1)

                    try:
                        im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, band)
                        im_data = np.where(im_data > 0, 1, 0)
                        # im_data = np.where(im_data < 0, -1, im_data)
                        # print(np.sum(im_data))
                        # amount_data = np.ma.masked_array(im_data,np.logical_not(im_data))
                        # print(year+":"+ daydir+":"+filename)
                        amount_data = amount_data + im_data
                        pic_num = pic_num + 1
                    except:
                        continue
    amount_data = np.where(amount_data > 0, amount_data.astype(int), np.nan)
    # amount_data = np.where(amount_data >= 0, (amount_data/pic_num).astype(float), np.nan)
    # 保存计算结果，不需要每次都计算
    Modis_IO.write_img(os.path.join(root_path, 'results', 'RHF', year + '.tif'), im_proj, im_geotrans, amount_data)
    print('days:', pic_num)

    # DisAsHist(amount_data)
    # Statics(amount_data)
    # DisAsImage(amount_data)


def RHF(root_path, year, time='day', orig_file='result.tif'):
    """
    计算相对高温频次
    :param root_path:文件路径
    :param year: 年份
    :return:
    """
    # amount_data = np.zeros((2400, 2400))
    data_path = os.path.join(root_path, 'mosic' + year)
    amount_data = np.zeros((1221, 2224))
    band = 1
    # amount_data = np.where(amount_data == 0, np.nan, 0)
    pic_num = 0
    im_proj = ''
    im_geotrans = ''

    for roots, dir, file in os.walk(data_path):
        # print (dir)
        for daydir in dir:
            rootPaths = os.path.join(data_path, daydir, time)
            # print(root_path)
            for root, dirs, files in os.walk(rootPaths):
                if orig_file in files:
                    filename = os.path.join(rootPaths, orig_file)
                    # print(filename)

                    # Station_Modis_ETL.get_grid_value_by_station_value(root_path, filename,year,daydir,band=1)

                    try:
                        im_data, im_geotrans, im_proj = Modis_IO.read_img(filename, band)
                        im_data = np.where(im_data > 0, im_data, np.nan)
                        im_data_mean = np.nanmean(im_data)
                        im_data_F = np.where(im_data > im_data_mean, 1, np.nan)
                        Modis_IO.write_img(os.path.join(rootPaths, 'RHF.tif'), im_proj, im_geotrans, im_data_F)
                        print(os.path.join(rootPaths, 'RHF.tif') + "done!")
                    except:
                        continue

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
    begin_year = 2003
    end_year = 2019
    im_proj = ''
    im_geotrans = ''
    for i in range(begin_year, end_year):
        year = str(i)
        # RHF(root_path, year)
        # EveryPoint(root_path, year)


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


#FuncTest()
def RHF_cluster():
    root_path = Common_func.UsePlatform()
    im_proj = ''
    im_geotrans = ''
    data_path = os.path.join(root_path, 'results', 'days')
    amount_data = []
    im_data = []
    for i in range(2003,2019):
        file = str(i) + '.tif'
        im_data, im_geotrans, im_proj = Modis_IO.read_img(os.path.join(data_path, file), 1)
        im_data = np.where(im_data >0 , im_data, np.nan)
        amount_data.append(im_data.flatten())
    #amount_data = np.array(amount_data).T
    #amount_data = np.nan_to_num(amount_data)
    data = pd.DataFrame(amount_data).add_prefix("col")
    data.profile_report(title='Pandas Profiling Report').to_file(output_file="output.html")
    #amount_data  = np.nanmean(amount_data, axis=0).reshape(1221,2224)
    #amount_data = feature_cluster(im_data)
    #Modis_IO.write_img(os.path.join(data_path, '2003-2018_mean.tif'), im_proj, im_geotrans, amount_data)
#RHF_cluster()

#data = os.path.join(Common_func.UsePlatform(),'stations','hour-sum-mask.tif')
#im_data, im_geotrans, im_proj = Modis_IO.read_img(data, 1)
#im_data = np.where(im_data>0,im_data,np.nan)
#im_data = feature_cluster(im_data)
#Modis_IO.write_img(os.path.join(Common_func.UsePlatform(), 'stations','hour-sum-mask_cluster.tif'),im_proj,im_geotrans,im_data)

station_hours = os.path.join(Common_func.UsePlatform(), 'stations','hour-sum-mask_cluster_final.tif')
modis_hours = os.path.join(Common_func.UsePlatform(),'results','RHD','2003-2018.tif')
im_data_S, im_geotrans, im_proj = Modis_IO.read_img(station_hours, 1)
im_data_M, im_geotrans, im_proj = Modis_IO.read_img(modis_hours, 1)
im_data_S = im_data_S.flatten()
im_data_M = im_data_M.flatten()
#im_data_S = np.where(im_data_S<-2,np.nan,im_data_S)
final_result = np.zeros(im_data_M.shape).flatten()
row = 1221
col = 2224
lenth = row*col
for i in range(0,lenth):
    #tem = im_data_M[i]
    if np.isnan(im_data_M[i]):
        final_result[i] = np.nan
    else:
        M = im_data_M[i]
        S = im_data_S[i]
        if (M < 0) & (S <= 0):
            final_result[i] = 1
        if (M >= 0) & (S < 0):
            final_result[i] = 2
        if (M == 0) & (S ==0):
            final_result[i] = 3
        if (M <= 0) & (S >0):
            final_result[i] = 4
        if (M > 0) & (S >=0):
            final_result[i] = 5
        print(S,M,final_result[i])
final_result = final_result.reshape(1221,2224)
#final_result = np.where((im_data_M<0)&(im_data_S<0),1,final_result)
#final_result = np.where((im_data_M>0)&(im_data_S<0),2,final_result)
#final_result = np.where((im_data_M==0)&(im_data_S==0),3,final_result)
#final_result = np.where((im_data_M<0)&(im_data_S>0),4,final_result)
#final_result = np.where((im_data_M>0)&(im_data_S>0),5,final_result)
#final_result = np.where(final_result == 0, np.nan, final_result)
Modis_IO.write_img(os.path.join(Common_func.UsePlatform(),'results','final2.tif'),im_proj,im_geotrans,final_result)
