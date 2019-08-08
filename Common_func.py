import platform

def UsePlatform():
    """
    工作平台包括windows和mac
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
        root_path = '/home/seedserver/mosicData/'
    #print (root_path)
    return root_path

UsePlatform()