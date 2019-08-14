import pandas
import Common_func
import os
import point_from_grid as pfg

def get_grow_stage_by_lonlat(root_path,lon,lat,stage):
    #stage_tif_path = os.path.join(root_path,stage)
    test_file = os.path.join(root_path,'grow_peroid_data',stage,'CX.0.tif')
    #for root, dirs,files in os.walk(stage_tif_path):
    stage_day = pfg.get_value_by_coordinates(test_file,[lon,lat],band=1)
    return stage_day

def aro_stage_ETL(root_path,grow_stage):
    '''
    按年和生育阶段获取目标区内的点
    '''
    grow_stage_data =pandas.read_csv(os.path.join(root_path,'grow_peroid_data','grow_period_points.csv'))
    station_list = pandas.read_csv(os.path.join(root_path,'grow_peroid_data','agro_stations.csv'))
    start_year = 2001
    end_year = 2012
    for year in range(start_year, end_year):
        year_grow_stage_data = grow_stage_data[(grow_stage_data['yearID'] == year) & (grow_stage_data['growthStage'] ==grow_stage)]
        for stationID in year_grow_stage_data['AgoStationID']:
            grow_stage_day = year_grow_stage_data[year_grow_stage_data['AgoStationID'] == stationID]['growthDate'].values[0]
            lon = float(station_list[station_list['区站号'] == stationID]['经度'].values[0])
            lat = float(station_list[station_list['区站号'] == stationID]['纬度'].values[0])
            print(stationID,lon,lat,year,grow_stage,Common_func.yyyymmdd_to_day_num(grow_stage_day))

def funTest():
    root_path = Common_func.UsePlatform()

    #data_file =os.path.join(root_path, 'grow_peroid_data', 'grow_period_points.csv')
    #grow_period_data = pandas.read_csv(data_file)
    #year_list = grow_period_data['yearID'].unique()
    #for year in year_list:
    #    year_grow_period_data = grow_period_data[grow_period_data['yearID'] == year]
    #    print(year_grow_period_data['growthDate'].values)

    # 发现别人插值的没有SpatialReference,还是要自己插值一遍
    # todo 下一步要实现 调一下QGIS的插值API,做操作，参考：
    # https://gis.stackexchange.com/questions/100188/how-to-compute-an-interpolation-raster-from-the-python-console-in-qgis/233322#233322
    station_list =pandas.read_csv(os.path.join(root_path,'HHHstations.csv'))
    for index, lonlatdata in station_list.iterrows():
        try:
            lon = float(lonlatdata['Longitude'])
            lat = float(lonlatdata['Latitude'])
            StationID = lonlatdata['StationID']
            stage_day = get_grow_stage_by_lonlat(root_path,lon,lat,stage='CX')
            print (round(stage_day))
        except:
            print('no data')

    #aro_stage_ETL(root_path,'抽雄')

funTest()