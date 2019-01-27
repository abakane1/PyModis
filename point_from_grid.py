# coding:utf-8

import numpy as np
from osgeo import gdal
from osgeo import osr


def get_file_info(in_file_path):
    '''

    :param in_file_path:
    :return: 数据集，地理坐标，投影坐标，栅格
    '''
    #

    pcs = None
    gcs = None
    shape = None

    #

    if in_file_path.endswith(".tif") or in_file_path.endswith(".TIF"):
        dataset = gdal.Open(in_file_path)
        pcs = osr.SpatialReference()
        pcs.ImportFromWkt(dataset.GetProjection())
        gcs = pcs.CloneGeogCS()
        extend = dataset.GetGeoTransform()
        shape = (dataset.RasterXSize, dataset.RasterYSize)
    else:
        raise ("Unsupported file format!")

    return dataset, gcs, pcs, extend, shape


def lonlat_to_xy(gcs, pcs, lon, lat):
    ct = osr.CoordinateTransformation(gcs, pcs)
    coordinates = ct.TransformPoint(lon, lat)

    return coordinates[0], coordinates[1], coordinates[2]


def xy_to_lonlat(gcs, pcs, x, y):
    ct = osr.CoordinateTransformation(pcs, gcs)
    lon, lat, _ = ct.TransformPoint(x, y)
    return lon, lat


def xy_to_rowcol(extend, x, y):
    a = np.array([[extend[1], extend[2]], [extend[4], extend[5]]])
    b = np.array([x - extend[0], y - extend[3]])
    row_col = np.linalg.solve(a, b)  # 二元一次方程求解
    row = int(np.floor(row_col[1]))
    col = int(np.floor(row_col[0]))

    return row, col


def rowcol_to_xy(extend, row, col):
    x = extend[0] + row * extend[1] + col * extend[2]
    y = extend[3] + row * extend[4] + col * extend[5]

    return x, y


def get_value_by_coordinates(file_path, coordinates, coordinates_type="lonlat"):
    dataset, gcs, pcs, extend, shape = get_file_info(file_path)
    img = dataset.GetRasterBand(1).ReadAsArray()
    value = None

    if coordinates_type == 'rowcol':
        value = img[coordinates[0], coordinates[1]]
    elif coordinates_type == 'lonlat':
        x, y, _ = lonlat_to_xy(gcs, pcs, coordinates[0], coordinates[1])
        row, col = xy_to_rowcol(extend, x, y)
        value = img[row, col]
    elif coordinates_type == 'xy':
        row, col = xy_to_rowcol(extend, coordinates[0], coordinates[1])
        value = img[row, col]
    else:
        raise ('wrong input!')

    return value

def set_value_by_coordinates(file_path, grid_value_list):
    dataset, gcs, pcs, extend, shape = get_file_info(file_path)
    img = dataset.GetRasterBand(1).ReadAsArray()
    for index, grid_value in grid_value_list.iterrows():
        try:
            lon = float(grid_value['Longitude'])
            lat = float(grid_value['Latitude'])
            x, y, _ = lonlat_to_xy(gcs, pcs, lon, lat)
            row, col = xy_to_rowcol(extend, x, y)
            img[row, col] = int(grid_value['grid_value'])
            print(file_path, ",", row, ",", col, ",", int(grid_value['grid_value']), 'done!')
        except:
            print('wrong input!')
    return img, extend, pcs
#root_path = "/Volumes/Data/newmosicData/"
#year = '2007'
#file_path = root_path + 'result' + year + '.tif'
#pixel_value = get_value_by_coordinates(file_path, [113.88333, 35.31667])
#print(pixel_value)
