# coding:utf-8
from osgeo import gdal


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

# 结果，存储为txt，分隔号为，
def write_txt(filename, row):
    # 以写的方式打开文件，如果文件不存在，就会自动创建
    file_write_obj = open(filename, 'a')
    file_write_obj.writelines(row)
    file_write_obj.write('\n')
    file_write_obj.close()