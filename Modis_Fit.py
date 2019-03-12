# coding:utf-8
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics


try:
    from osgeo import ogr
except:
    import ogr


def display_as_scatter(x,y):
    plt.xlabel("grid_value")
    plt.ylabel("station_value")
    plt.scatter(x, y)
    plt.show()


def display_as_ROC(y_pred, y_test, title):
    # 做ROC曲线
    plt.figure()
    plt.plot(range(len(y_pred)), y_pred, 'b', label="predict")
    plt.plot(range(len(y_pred)), y_test, 'r', label="test", alpha=0.5)
    # plt.scatter(y_pred, y_test)
    plt.legend(loc="upper right")  # 显示图中的标签
    plt.xlabel("range")
    plt.ylabel('values')
    plt.title(str(title))
    plt.show()


def fit(fit_range='station', fit_method='numpy'):
    data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/station-grid copy.csv')
    data = data[(data['grid_value'] < 500) & (data['station_value'] < 500) & (data['grid_value'] > 0) & (
            data['station_value'] > 0)]
    if fit_range == 'station':
        station_list = data['stationID'].unique()
        for station in station_list:
            station_value = data[data['stationID'] == station]
            x = station_value['grid_value'].values
            y = station_value['station_value'].values
            if fit_method == 'sklearn':
                a, b, RMSE, R2 = multi_linear_fit(x, y)
            else:
                a, b, RMSE, R2 = linear_fit(x, y)
    if fit_range == 'year':
        for year in range(2003, 2015):
            station_value = data[data['year'] == year]
            x = station_value['grid_value'].values
            y = station_value['station_value'].values
            if fit_method == 'sklearn':
                a, b, RMSE, R2 = multi_linear_fit(x, y)
            else:
                a, b, RMSE, R2 = linear_fit(x, y)
    else:
        y = data['grid_value'].values
        x = data['station_value'].values
        if fit_method == 'sklearn':
            a, b, RMSE, R2 = multi_linear_fit(x, y)
        else:
            a, b, RMSE, R2 = linear_fit(x, y)

    # display_as_scatter(data)
    return a, b, RMSE, R2


# 线性回归-numpy
def linear_fit(x, y):
    f1 = np.polyfit(x, y, 1)
    p1 = np.poly1d(f1)
    # fit values, and mean
    yhat = p1(x)  # or [p(z) for z in x]
    RMSE = np.sqrt(np.mean((yhat - y) ** 2))
    ybar = np.sum(y) / len(y)  # or sum(y)/len(y)
    ssreg = np.sum((yhat - ybar) ** 2)  # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar) ** 2)  # or sum([ (yi - ybar)**2 for yi in y])
    # print('a:', f1[0], 'b:', f1[1], 'r2:', ssreg / sstot)
    print(f1[0], f1[1], RMSE, ssreg / sstot)
    display_as_scatter(x, y)
    return f1[0], f1[1], RMSE, ssreg / sstot


# 线性回归- sklearn train:test = 8:2
def multi_linear_fit(x, y):
    # data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/staion-grid-withlanlon.csv')
    # data = data[(data['grid_value'] > 0) & (data['station_value'] > 0) & (data['stationid'] == 53898)]
    X = np.array(x).reshape(-1, 1)
    # y = pd.factorize(data.loc[:,'grid_value'].values)[0].reshape(-1, 1)
    # print(year)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)
    # print('X_train.shape={}\n y_train.shape ={}\n X_test.shape={}\n,  y_test.shape={}'.format(X_train.shape,y_train.shape,X_test.shape,y_test.shape))
    linreg = LinearRegression()
    model = linreg.fit(X, y)
    # 训练后模型截距
    b = linreg.intercept_
    # 训练后模型权重（特征个数无变化）
    a = linreg.coef_[0]
    # 预测
    y_pred = linreg.predict(X_test)
    # print(y_pred)
    # calculate RMSE by hand
    RMSE = metrics.mean_absolute_error(y_test, y_pred)
    # print(metrics.mean_squared_error(y_test, y_pred))
    R2 = metrics.r2_score(y_test, y_pred)
    display_as_scatter(x, y)
    print(a, b, RMSE, R2)
    return a, b, RMSE, R2


#a, b, RMSE, R2 = fit(fit_range='station', fit_method='numpy')
