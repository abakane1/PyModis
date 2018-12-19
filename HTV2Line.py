
# coding:utf-8
from osgeo import gdal
import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show_hist
import pyhdf.SD as hdf


class GRID:

    #读图像文件
    def read_img(self,filename):
        dataset=gdal.Open(filename)       #打开文件
        im_width = dataset.RasterXSize    #栅格矩阵的列数
        im_height = dataset.RasterYSize   #栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  #仿射矩阵
        im_proj = dataset.GetProjection() #地图投影信息
        im_data = dataset.ReadAsArray(0,0,im_width,im_height) #将数据写成数组，对应栅格矩阵
        bandda = dataset.GetRasterBand(5)
        a = bandda.ReadAsArray(0, 0, im_width, im_height)
        b = np.where(a > 0, a, 0)



        del dataset
        return im_proj,im_geotrans,b

    # 34度阈值计算(分子)

    def readThreshold(self, filename):
        dataset = gdal.Open(filename)  # 打开文件
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
        im_proj = dataset.GetProjection()  # 地图投影信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵
        bandda = dataset.GetRasterBand(1)
        a = bandda.ReadAsArray(0, 0, im_width, im_height)
        daydata = np.fromstring(a, np.int16)
        daydatanp = np.reshape(daydata, [im_width, im_height]).astype(np.int16)
        daysum= np.sum(a,dtype=np.int64)
        n =  daydatanp != 0
        z = daydatanp[n]
        dayNumber = z.size
        dayMean  = daysum/dayNumber
        b = np.where(a > 15307, 0.02 * a - 273.15-(0.02*dayMean-273.15), 0)

        del dataset
        return im_proj, im_geotrans, b

    # 白天温度-夜晚温度计算(分母)

    def readDenominator(self, filename):
        dataset = gdal.Open(filename)  # 打开文件
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
        im_proj = dataset.GetProjection()  # 地图投影信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵
        bandda = dataset.GetRasterBand(1)
        nightbandda = dataset.GetRasterBand(5)
        a = bandda.ReadAsArray(0, 0, im_width, im_height)
        nighta = nightbandda.ReadAsArray(0, 0, im_width, im_height)


        daydata = np.fromstring(a, np.int16)
        daydatanp = np.reshape(daydata, [im_width, im_height]).astype(np.int16)
        nightdata = np.fromstring(nighta, np.int16)
        nightdatanp = np.reshape(nightdata, [im_width, im_height]).astype(np.int16)
        b = np.where(daydatanp > 15307, daydatanp, 0)
        print(b.shape)
        c = np.where(nightdatanp > 0, nightdatanp, 0)
        print(c.shape)
        #c = np.where(a > 15307, nighta, 0)
        #nightb = np.where(nighta > 0, nighta,0)

        dayNightDifference = np.subtract(b,c).astype(np.int16)
        #dayNightDifference = np.subtract(b, nightb,dtype='i2')
        npdiff = np.where(dayNightDifference>0,0.02 * dayNightDifference - 273.15,0)

        del dataset
        return im_proj, im_geotrans, npdiff
        # 时间标量化

    def readDays(self, filename):
        dataset = gdal.Open(filename)  # 打开文件
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
        im_proj = dataset.GetProjection()  # 地图投影信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵
        bandda = dataset.GetRasterBand(5)
        a = bandda.ReadAsArray(0, 0, im_width, im_height)
        b = np.where(a > 14907, 1, 0)

        del dataset
        return im_proj, im_geotrans, b

        # 读图像文件并进行归一化

    def readNormalize(self, filename):
        dataset = gdal.Open(filename)  # 打开文件
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数

        im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
        im_proj = dataset.GetProjection()  # 地图投影信息
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵
        bandda = dataset.GetRasterBand(1)
        a = bandda.ReadAsArray(0, 0, im_width, im_height)
        b = np.where(a > 0, a, 0)
        temMax = b.max()
        temMin = b.min()
        c = np.where(b > 0, (b - temMin) / (temMax - temMin), 0)
        del dataset
        return im_proj, im_geotrans, c


    #写文件，以写成tif为例
    def write_img(self,filename,im_proj,im_geotrans,b):
        #gdal数据类型包括
        #gdal.GDT_Byte,
        #gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
        #gdal.GDT_Float32, gdal.GDT_Float64

        #判断栅格数据的数据类型
        if 'int8' in b.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in b.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        #判读数组维数
        if len(b.shape) == 3:
            im_bands, im_height, im_width = b.shape
        else:
            im_bands, (im_height, im_width) = 1,b.shape

        #创建文件
        driver = gdal.GetDriverByName("GTiff")            #数据类型必须有，因为要计算需要多大内存空间
        dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

        dataset.SetGeoTransform(im_geotrans)              #写入仿射变换参数
        dataset.SetProjection(im_proj)                    #写入投影

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(b)  #写入数组数据
        else:
            for i in range(im_bands):
                dataset.GetRasterBand(i+1).WriteArray(b[i])

        del dataset

    def display_img(self,path):

        ## matplob
        #im = plt.imshow(b)
        #plt.colorbar(im)
        #plt.show()

        ## rasterio
        src = rasterio.open(path+"/htAccumulation.tif")
        plt.imshow(src.read(1), cmap='pink')

        plt.show()

        show_hist(src, bins=50, lw=0.0, stacked=False, alpha=0.3, histtype='stepfilled', title="Histogram")

    def HTcalculation(self,path,amountPath):

        for root, dirs, files in os.walk(path):
            #print(files)
            amountData = np.zeros((1200, 1200))
            for LST in files:
                if os.path.splitext(LST)[1] == ".tif":
                    run = GRID()
                    proj, geotrans, data = run.readThreshold(path+"/" +LST)

                    diffproj, diffprojgeotrans, diffData = run.readDenominator(path + "/" + LST)
                    cccc = np.divide(data, diffData, out=np.zeros_like(data), where=diffData != 0)
                    #modelData = (data*1000)/diffData
                    amountData = amountData + cccc
            run.display_img(proj,geotrans,amountData)
            #os.chdir(amountPath)  # 切换路径到待处理图像所在文件夹
            #run.write_img("htAccumulation.tif", proj, geotrans, amountData)  # 写数据

            print("高温积害量计算完成")
            break

    def overlayCalculation(self,Path,daysPath):
        folder = os.path.exists(daysPath)
        if not folder:
            os.mkdir(daysPath)
            for root, dirs, files in os.walk(Path):
                c = np.zeros((1200, 1200))
                # if os.path.splitext(files)[1] == '.tif':
                for LST in files:
                    if os.path.splitext(LST)[1] == ".tif":
                        proj, geotrans, data = run.readDays(Path+"\\" + LST)  # 读数据
                        c = c + data
                os.chdir(daysPath)  # 切换路径到待处理图像所在文件夹
                run.write_img("htDasys.tif", proj, geotrans, c)  # 写数据
                print("时间叠加计算完成")
                break

        else:
            for root, dirs, files in os.walk(Path):
                c = np.zeros((1200, 1200))
                # if os.path.splitext(files)[1] == '.tif':
                for LST in files:
                    if os.path.splitext(LST)[1] == ".tif":
                        proj, geotrans, data = run.readDays(Path+"\\" + LST)  # 读数据
                        c = c + data
                os.chdir(daysPath)  # 切换路径到待处理图像所在文件夹
                run.write_img("htDasys.tif", proj, geotrans, c)  # 写数据
                print("时间叠加计算完成")
                break

    def resultCauculate(self,amountPath,daysPath,resultPath):

        folder = os.path.exists(resultPath)
        if not folder:
            os.mkdir(resultPath)
            proj, geotrans, data1 = run.readNormalize(amountPath + "\\" + "htAccumulation.tif")  # 读数据
            proj1, geotrans1, data2 = run.readNormalize(daysPath + "\\" + "htDasys.tif")  # 读数据

            c = 0.7 * data1 + 0.3 * data2

            os.chdir(resultPath)  # 切换路径到待处理图像所在文件夹
            run.write_img("result.tif", proj, geotrans, c)  # 写数据
            print("结果计算完成")


        else:
            proj, geotrans, data1 = run.readNormalize(amountPath + "\\" + "htAccumulation.tif")  # 读数据
            proj1, geotrans1, data2 = run.readNormalize(daysPath + "\\" + "htDasys.tif")  # 读数据

            c = 0.8 * data1 + 0.2 * data2

            os.chdir(resultPath)  # 切换路径到待处理图像所在文件夹
            run.write_img("result.tif", proj, geotrans, c)  # 写数据
            print("结果计算完成")



if __name__ == "__main__":
    rootPath = "/Volumes/Data/hxlHT"
    for root, dirs, files in os.walk(rootPath):
        starttime = datetime.datetime.now()
        for dirName in dirs:
            if dirName == "data2015":

                path = root+"/"+dirName
                tiffPath = path + "/" + "nighttotiff"
                amountPath = path + "/" +"modleaccumulation"
                daysPath = path + "/" +"nightdays"
                resultPath = path + "/" +"nightresult"
                run = GRID()

                #run.HTcalculation(tiffPath, amountPath)
                #run.overlayCalculation(tiffPath,daysPath)
                #run.resultCauculate(amountPath,daysPath,resultPath)
                run.display_img(amountPath)
        endtime = datetime.datetime.now()
        print((endtime - starttime).seconds)
        break
