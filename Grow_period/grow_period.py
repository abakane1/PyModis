import pandas
import Common_func
import os
import point_from_grid as pfg
import Modis_IO
import math

def get_heat_stress_hours_every_station(root_path, stationID,station_name,lon,lat, year, stage_start_day, stage_end_day, heat_temperature,result_file):
    #heat_temperature =heat_temperature*10
    meteo_data = pandas.read_csv(os.path.join(root_path, 'stationdata.csv'))
    for day_num in range(stage_start_day,stage_end_day):
        fu, month, day = Common_func.day_num_to_yyyymmdd(year, day_num)
        heat_days = meteo_data[(meteo_data['StationID'] == stationID) & (meteo_data['Year'] == year) & (
                meteo_data['Months'] == month) & (meteo_data['Days'] == day) & (
                                       meteo_data['HighestTemperature'] >= heat_temperature)]
        if heat_days.empty:
            print(station_name+' '+str(year)+' ' +str(day_num)+' '+'no heat!')
            continue
        else:
            try:
                # 高温时长模型实现
                # 参数 太阳赤纬
                sun_chiwei  = 0.39795*math.cos(0.98563*(day_num-173))
                T_max = heat_days['HighestTemperature'].values[0]/10
                T_min = heat_days['LowestTemperature'].values[0]/10
                # fix a bug 天数-1 之后转日期，不能直接日-1 会报错
                fu_next,month_next,day_next = Common_func.day_num_to_yyyymmdd(year,day_num+1)
                T_min_tomorrow = meteo_data[(meteo_data['StationID'] == stationID) & (meteo_data['Year'] == year) & (
                    meteo_data['Months'] == month_next) & (meteo_data['Days'] == day_next)]['LowestTemperature'].values[0]/10

                a = math.sin(lat)*math.sin(sun_chiwei)
                b = math.cos(lat)*math.cos(sun_chiwei)
                DL = 12* (1+(2/math.pi)*a*(math.sin(a/b)))
                p = 2
                heat_temperature_real = heat_temperature/10
                A1 = math.asin((heat_temperature_real-T_min)/(T_max-T_min))
                A2 = math.asin((heat_temperature_real-T_min_tomorrow)/(T_max-T_min_tomorrow))
                heat_stress_hours = (DL+2*p)*(1-(A1+A2)/math.pi)
                row = str(stationID) + ' ' + station_name + ' ' + str(lon) + ' ' + str(lat) + ' ' + str(year) + ' ' + str(
                        round(stage_start_day)) + ' ' + str(round(stage_end_day))+' '+ str(day_num)+ ' '+str(heat_temperature_real)+' '+ str(format(heat_stress_hours,'2f'))
                print(row)
                Modis_IO.write_txt(result_file, row)
            except:
                continue


# todo 定义一个生育期得字典，重构硬编码
#   由于论文目前就分析抽雄
def get_grow_stage_by_lonlat(root_path, lon, lat, year, stage):
    """
    从插值结果中根据经纬度信息提出对应的生育期时间起止
    :param root_path:根路径
    :param lon: 经度
    :param lat: 纬度
    :param year: 年份
    :param stage: 生育阶段
    :return: 起始日期 default 抽雄期（）
    """
    stage_start_file = os.path.join(root_path, 'grow_peroid_data', stage, year + '.tif')
    end_stage = 'RS'
    stage_end_file = os.path.join(root_path, 'grow_peroid_data', end_stage, year + '.tif')
    # for root, dirs,files in os.walk(stage_tif_path):
    stage_start_day = pfg.get_value_by_coordinates(stage_start_file, [lon, lat], band=1)
    stage_end_day = pfg.get_value_by_coordinates(stage_end_file, [lon, lat], band=1)
    return stage_start_day, stage_end_day


def aro_stage_ETL(root_path, grow_stage):
    '''
    按年和生育阶段获取目标区内的点
    '''
    grow_stage_data = pandas.read_csv(os.path.join(root_path, 'grow_peroid_data', 'grow_period_points.csv'))
    station_list = pandas.read_csv(os.path.join(root_path, 'grow_peroid_data', 'agro_stations.csv'))
    start_year = 2001
    end_year = 2014
    for year in range(start_year, end_year):
        result_file = os.path.join(root_path, 'grow_peroid_data', 'RS', str(year) + '.txt')
        first_row = 'stationID Longitude Latitude year grow_stage grow_date'
        Modis_IO.write_txt(result_file, first_row)
        year_grow_stage_data = grow_stage_data[
            (grow_stage_data['yearID'] == year) & (grow_stage_data['growthStage'] == grow_stage)]
        for stationID in year_grow_stage_data['AgoStationID']:
            grow_stage_day = \
            year_grow_stage_data[year_grow_stage_data['AgoStationID'] == stationID]['growthDate'].values[0]
            lon = float(station_list[station_list['区站号'] == stationID]['经度'].values[0])
            lat = float(station_list[station_list['区站号'] == stationID]['纬度'].values[0])
            row = str(stationID) + ' ' + str(lon) + ' ' + str(lat) + ' ' + str(year) + ' ' + grow_stage + ' ' + str(
                Common_func.yyyymmdd_to_day_num(grow_stage_day))
            Modis_IO.write_txt(result_file, row)
        print(result_file)


def todofunction(root_path):
    # 发现别人插值的没有SpatialReference,还是要自己插值一遍
    # todo 为了论文进度，先手动都插值了一遍，等有空了自己调用api做一遍
    #  1.下一步要实现 调一下QGIS的插值API,做操作，参考：https://gis.stackexchange.com/questions/100188/how-to-compute-an-interpolation-raster-from-the-python-console-in-qgis/233322#233322
    # aro_stage_ETL(root_path,'乳熟')

    station_list = pandas.read_csv(os.path.join(root_path, 'HHHstations.csv'))
    result_file = (os.path.join(root_path, 'stations_cx.txt'))
    for index, lonlatdata in station_list.iterrows():
        try:

            lon = float(lonlatdata['Longitude'])
            lat = float(lonlatdata['Latitude'])
            StationID = lonlatdata['StationID']
            station_name = lonlatdata['StationName']
            for i in range(2001, 2014):
                year = str(i)
                stage_start_day, stage_end_day = get_grow_stage_by_lonlat(root_path, lon, lat, year, stage='CX')
                # print (round(stage_start_day),round(stage_end_day))
                fu, start_month, start_day = Common_func.day_num_to_yyyymmdd(year, stage_start_day)
                fu, end_month, end_day = Common_func.day_num_to_yyyymmdd(year, stage_end_day)
                row = str(StationID) + ' ' + station_name + ' ' + str(lon) + ' ' + str(lat) + ' ' + year + ' ' + str(
                    round(stage_start_day)) + ' ' + str(round(stage_end_day))
                print(row)
                #Modis_IO.write_txt(result_file, row)
        except:
            print('no data')


def funTest():
    root_path = Common_func.UsePlatform()
    station_list = pandas.read_csv(os.path.join(root_path, 'HHHstations.csv'))
    station_stage_list =pandas.read_csv(os.path.join(root_path,'stations_cx_back.txt'),' ')
    result_file = (os.path.join(root_path, 'stations_heat_stress_hours.txt'))
    for index, lonlatdata in station_list.iterrows():
        lon = float(lonlatdata['Longitude'])
        lat = float(lonlatdata['Latitude'])
        stationID = lonlatdata['StationID']
        station_name = lonlatdata['StationName']
        for i in range(2001, 2014):
            year = str(i)
            stage_start_day = int(station_stage_list[(station_stage_list['year'] == i) & (station_stage_list['stationID'] == stationID)]['cx_start'].values[0])
            stage_end_day = int(station_stage_list[(station_stage_list['year'] == i) & (station_stage_list['stationID'] == stationID)]['cx_end'].values[0])
            get_heat_stress_hours_every_station(root_path,stationID,station_name,lon,lat,i,stage_start_day,stage_end_day,340,result_file)


    # data_file =os.path.join(root_path, 'grow_peroid_data', 'grow_period_points.csv')
    # grow_period_data = pandas.read_csv(data_file)
    # year_list = grow_period_data['yearID'].unique()
    # for year in year_list:
    #    year_grow_period_data = grow_period_data[grow_period_data['yearID'] == year]
    #    print(year_grow_period_data['growthDate'].values)
#root_path = Common_func.UsePlatform()
#get_heat_stress_hours_every_station(root_path, 54909,'定陶',115.55,35.1, 2004, 212, 241,340,'')


funTest()
