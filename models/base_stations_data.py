import pandas
import Common_func
import os
import Modis_IO
import math
import pandas as pd
import  stations.Station_ETL
import  Grow_period.grow_period
import pandas_profiling

def get_heat_stress_hours_every_station(root_path, stationID,station_name,lon,lat, year, stage_start_day, stage_end_day, heat_temperature,result_file):
    """
    计算每个点的高温时长
    :param root_path: 数据根目录
    :param stationID: 点id
    :param station_name: 点名字
    :param lon: 经度
    :param lat: 纬度
    :param year: 年份
    :param stage_start_day: 生育期起始日期
    :param stage_end_day: 生育期截至日期
    :param heat_temperature: 高温阈值
    :param result_file: 结果保存文件路径
    :return: 输出 输入参数+高温时长
    """
    #heat_temperature =heat_temperature*10
    meteo_data = pandas.read_csv(os.path.join(root_path, 'stationdata.csv'))
    sum_heat_days = 0
    sum_heat_hours = 0
    for day_num in range(stage_start_day,stage_end_day+1):
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
                sum_heat_hours = sum_heat_hours + heat_stress_hours
                sum_heat_days = sum_heat_days + 1
                row = str(stationID) + ' ' + station_name + ' ' + str(lon) + ' ' + str(lat) + ' ' + str(year) + ' ' + str(
                        round(stage_start_day)) + ' ' + str(round(stage_end_day))+' '+ str(day_num)+ ' '+str(T_max)+' '+ str(format(heat_stress_hours,'2f'))
                print(row)
                Modis_IO.write_txt(result_file, row)
            except:
                continue

    row = str(stationID) + ' ' + station_name + ' ' + str(lon) + ' ' + str(lat) + ' ' + str(year) + ' '  + str(sum_heat_days) + ' ' + str(
    format(sum_heat_hours, '2f'))
    file = str(year)+'.txt'
    Modis_IO.write_txt(file,row)

root_path = Common_func.UsePlatform()
def Cal(root_path):
    for i in range(2010,2019):
        year = i
        lonlatlist = pd.read_csv( os.path.join(root_path,'HHHstations.csv'))
        for index, lonlatdata in lonlatlist.iterrows():
            try:
                lon = float(lonlatdata['Longitude'])
                lat = float(lonlatdata['Latitude'])
                stationID = lonlatdata['StationID']
                station_name = stations.Station_ETL.get_station_name_by_stationID(stationID)
                cx_data = pd.read_csv(Common_func.cx, " ")
                stage_start_day = 152
                stage_end_day = 244
            #if year < 2014:
            #    stage_start_day = int(cx_data[((cx_data['stationID'] == stationID) & (cx_data['year'] == year))]['cx_start'].values[0])
            #    stage_end_day = int(cx_data[((cx_data['stationID'] == stationID) & (cx_data['year'] == year))]['cx_end'].values[0])
            #else:
            #    stage_start_day = int(
            #        cx_data[((cx_data['stationID'] == stationID) & (cx_data['year'] == 2013))]['cx_start'].values[0])
            #    stage_end_day = int(
            #        cx_data[((cx_data['stationID'] == stationID) & (cx_data['year'] == 2013))]['cx_end'].values[0])
                get_heat_stress_hours_every_station(root_path,stationID,station_name,lon,lat,year,stage_start_day,stage_end_day,340,'cx_every_day_hear_hour.txt')
            except:
                continue
#Cal(root_path)
data = pd.read_csv(os.path.join(root_path,'stations','times-stations-all-no-zero.csv'))
data.profile_report(title='Pandas Profiling Report').to_file(output_file="output-times.html")