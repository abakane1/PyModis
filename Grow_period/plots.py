import Common_func
import pandas as pd
import os




def test_fun():
    cx_data=pd.read_csv(cx," ")
    for index,station_data in pd.read_csv(HHH_stations_list).iterrows():
        lon = float(station_data['Longitude'])
        lat = float(station_data['Latitude'])
        stationID = int(station_data['StationID'])
        station_name = station_data['StationName']
        stage_ave_start_day = int(cx_data[cx_data['stationID'] == stationID]['cx_start'].mean())
        print(stationID,station_name,lon,lat,stage_ave_start_day)


root_path = Common_func.UsePlatform()
HHH_stations_list = Common_func.HHH_stations_list
cx = Common_func.cx

test_fun()
