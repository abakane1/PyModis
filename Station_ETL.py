import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Common_func

root_path = Common_func.UsePlatform()
station_list = pd.read_csv(os.path.join(root_path, 'HHHstations.csv'))
#print(os.path.join(root_path,'HHHstations.csv'))

data = pd.read_csv(os.path.join(root_path,'meteodata.csv'))

x = []
y = []
for index,station_data in station_list.iterrows():
    station_ID = station_data['StationID']
    station_name = station_data['StationName']
    year_list = data[data['StationID'] == station_ID]['Year'].unique()
    # print(station_ID,year_list)
    print(station_ID,station_name,station_data['Latitude'],station_data['Longitude'],len(year_list))
    x.append(station_ID)
    y.append(len(year_list))
    #for year in year_list:
    #    x.append(station_name)
    #    y.append(year)
# 年际分布
#print(x,y)
#plt.scatter(x,y)
#plt.show()
