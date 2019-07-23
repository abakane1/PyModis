# coding:utf-8
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.svm import SVR
import Common_func,Modis_IO
import point_from_grid as pfg

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
    # data = pd.read_csv('/Users/zzl/PycharmProjects/PyModis/staion-grid-withlanlon-data.csv') # mac path
    data = pd.read_csv('D:\\abakane1\\PyModis\\staion-grid-withlanlon-data.csv')
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

# 支持向量回归
def svm_linear_fit(X,y):
    X = np.array(X).reshape(-1, 1)
    ###############################################################################
    # Fit regression model
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    y_rbf = svr_rbf.fit(X, y).predict(X)
    #y_lin = svr_lin.fit(X, y).predict(X)
    #y_poly = svr_poly.fit(X, y).predict(X)

    ###############################################################################
    # look at the results
    lw = 2
    plt.scatter(X, y, color='darkorange', label='data')
    #plt.hold('on')
    plt.plot(X, y_rbf, color='navy', lw=lw, label='RBF model')
    #plt.plot(X, y_lin, color='c', lw=lw, label='Linear model')
    #plt.plot(X, y_poly, color='cornflowerblue', lw=lw, label='Polynomial model')
    plt.xlabel('data')
    plt.ylabel('target')
    plt.title('Support Vector Regression')
    plt.legend()
    plt.show()



#  20190321 修改
#  1：根据每一个grid value的值model生成一个新的station value
#  2：最后生成一幅新的tif为完整的气温数据
def set_grid_value_by_model(filename, model='linear'):
     im_data, im_geotrans, im_proj = Modis_IO.read_img(filename,1)

     return im_data, im_geotrans, im_proj
#    Modis_IO.write_img(filename, im_proj, im_geotrans, im_data)



def funcTest():
    root_path = Common_func.UsePlatform()
    data_file=root_path + 'staion-grid-withlanlon-data-.csv'
    data = pd.read_csv(data_file)
    data = data[(data['grid_value'] < 500) & (data['station_value'] < 500) & (data['grid_value'] > 0) & (
            data['station_value'] > 0)]
    y = data['grid_value'].values
    X = data['station_value'].values
    linear_fit(X,y)
    #svm_linear_fit(X,y)
    #display_as_scatter(data)

funcTest()
# a, b, RMSE, R2 = fit(fit_range='station', fit_method='numpy')
#svm_linear_fit()