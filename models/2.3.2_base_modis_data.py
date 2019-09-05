import pandas as pd
import Common_func
import os
import Modis_IO
import math
import numpy as np
import cupy as cp

root_path = Common_func.UsePlatform()
result_path = os.path.join(root_path,'results','nights')
amount_data = np.zeros((1221,2224))
band =1
im_data_list = []
im_data_list_mean =[]
im_geotrans = None
im_proj = None
for year in range(2003,2019):
    filename = os.path.join(result_path,str(year)+'.tif')
    #print (filename)
    try:
        im_data,im_geotrans,im_proj = Modis_IO.read_img(filename,band)
        im_data_list.append(im_data.flatten())
    except:
        continue

im_data_list_std = np.nanstd(im_data_list,axis=0).reshape(1221,2224)
# cupy
#im_data_list = cp.asarray(im_data_list)
#im_data_list_std = cp.std(im_data_list,axis=0).reshape(1221,2224)
Modis_IO.write_img(os.path.join(result_path,'std_night.tif'),im_proj,im_geotrans,im_data_list_std)
