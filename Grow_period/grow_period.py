import pandas
import Common_func
import os
def funTest():
    root_path = Common_func.UsePlatform()
    data_file =os.path.join(root_path, 'grow_peroid_data', 'grow_period_points.csv')
    grow_period_data = pandas.read_csv(data_file)
    year_list = grow_period_data['yearID'].unique()
    for year in year_list:
        year_grow_period_data = grow_period_data[grow_period_data['yearID'] == year]
        print(year_grow_period_data['growthDate'].values)

funTest()