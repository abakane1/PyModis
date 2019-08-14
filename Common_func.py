import platform
import datetime

def UsePlatform():
    """
    工作平台包括windows,linux和mac
    读取数据要先判断
    :return: 数据root_path
    """
    root_path = ''
    sysstr = platform.system()
    if(sysstr == 'Windows'):
        root_path = 'G:\\mosicData\\'
    if(sysstr =='MacOS'):
        root_path = '/volumes/data/mosicData/'
    if (sysstr == 'Linux'):
        root_path = '/home/seedserver/mosicdata/'
    #print(root_path)
    return root_path

# UsePlatform()

def yyyymmdd_to_day_num(date_str):
    """

    :param date_str: e.g:2001/1/1
    :return: 第一天(1)
    """
    year, month,day = date_str.split('/')
    # print(year,month,day)
    sday = datetime.date(int(year),int(month),int(day))
    day_num = sday - datetime.date(sday.year - 1, 12, 31)
    return  day_num.days

def day_num_to_yyyymmdd(year,day_num):
    """

    :param year: 年份
    :param day_num: 当年第几天
    :return: fu,month，day 完整日期格式，月份和日
    """
    now_time = datetime.datetime(int(year), int('01'), int('01'))
    f = now_time + datetime.timedelta(days=int(day_num) - 1)
    month = f.month
    day = f.day
    fu = f.strftime('%Y%m%d')
    return fu,month, day


