import pandas
import Common_func
import os
import point_from_grid as pfg
import Modis_IO
import math


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
                        round(stage_start_day)) + ' ' + str(round(stage_end_day))+' '+ str(day_num)+ ' '+str(T_max)+' '+ str(format(heat_stress_hours,'2f'))
                print(row)
                Modis_IO.write_txt(result_file, row)
            except:
                continue