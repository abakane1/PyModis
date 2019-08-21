# coding:utf-8
import os
import numpy as np
import matplotlib.pyplot as plt
import Common_func,Modis_IO

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

def count_pecent():
    im_geotrans = ''
    im_proj = ''
    amount_data = np.zeros((1221, 2224))
    data_path =os.path.join(Common_func.UsePlatform(),'results','nights')
    for root, dirs,files in os.walk(data_path):
        for file in files:
            im_data, im_geotrans, im_proj = Modis_IO.read_img(os.path.join(data_path,file), 1)
            amount_data = amount_data+im_data
        amount_data = np.where(amount_data >= 0, (amount_data/16).astype(float), np.nan)
        np.around(amount_data,decimals=2)
        Modis_IO.write_img(os.path.join(data_path,'2003-2018.tif'),im_proj,im_geotrans,amount_data)

#count_pecent()