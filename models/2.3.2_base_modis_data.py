import pandas as pd
import Common_func
import os
import Modis_IO
import math
import numpy as np


root_path = Common_func.UsePlatform()
result_path = os.path.join(root_path,'results','days')
amount_data = np.zeros(1221,2224)
band =1
for year in range(2003,2019):
    filename = os.path.join(result_path,str(year)+'.tif')
    print (filename)