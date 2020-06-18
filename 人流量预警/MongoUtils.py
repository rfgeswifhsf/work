# -*- coding:utf8 -*-
import datetime
import logging
import os
import time
from math import ceil
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn import tree
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from wariningemail import email

def date_transor(datestr,days):
    '''
    2020-05-26 17:14:37
    获取datestr所表示时间的前days天日期
    :param datestr: 时间字符串
    :param days: 天数
    :return:
    '''
    y, m, d = datestr.split("-")
    date = datetime.date(int(y), int(m), int(d))
    date = date + datetime.timedelta(days=-days)
    return date

def model_train(data,suggest_people):
    '''
    :param data: 模型训练数据集，包含index_slide,count_list,index_after_time,part_one--->时间序列下标，时间序列总打卡数，下一个时刻的下标，建议游玩时间前半段打卡数。所谓前半段时间是指（前半段时间+未来预测时间=建议游玩时间）
    :param suggest_people: 建议游玩人数
    :return:
    '''
    X_train,Y_trian = data[0],data[1]
    X_train = np.reshape(X_train, (-1, 1))

    model = LinearRegression()
    model.fit(X_train, Y_trian)
    X_pre=data[2]

    pre=model.predict([[X_pre]])
    print('LR预测下一个十分钟：',ceil(pre))

    if ceil(pre)+data[3]>int(suggest_people):
        print('都别再来了，人可多了，都{}人了'.format(ceil(pre)+data[3]))
    else:
        print('没事，可劲打卡，只有{}人'.format(ceil(pre)+data[3]))

    # 评估
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import mean_absolute_error
    import matplotlib.pyplot as plt
    y_pre = model.predict(X_train)
    # MSE
    mse_predict = mean_squared_error(Y_trian, y_pre)
    # MAE
    mae_predict = mean_absolute_error(Y_trian, y_pre)

    print('mse_predict: ',mse_predict)
    print('mae_predict: ',mae_predict)

    plt.scatter(X_train,Y_trian)
    plt.plot(X_train,y_pre,'r-')
    plt.show()

    return model,pre
def model_train_ARIMA(data,suggest_people):
    '''
    :param data: 模型训练数据集，包含index_slide,count_list,index_after_time,part_one--->时间序列下标，时间序列总打卡数，下一个时刻的下标，建议游玩时间前半段打卡数。所谓前半段时间是指（前半段时间+未来预测时间=建议游玩时间）
    :param suggest_people: 建议游玩人数
    :return:
    '''
    X_train,Y_trian = data[0],data[1]
    X_train = np.reshape(X_train, (-1, 1))

    from statsmodels.tsa.arima_model import ARIMA

    # 所以可以建立ARIMA 模型，ARIMA(0,1,1)
    model = ARIMA(Y_trian, (0, 1, 1)).fit()
    pre = model.forecast(1)  # 为未来5天进行预测， 返回预测结果， 标准误差， 和置信区间
    print('AR预计',ceil(pre[0]))


    if ceil(pre[0])+data[3]>int(suggest_people):
        print('都别再来了，人可多了，都{}人了'.format(ceil(pre[0])+data[3]))
    else:
        print('没事，可劲打卡，只有{}人'.format(ceil(pre[0])+data[3]))

    # # 评估
    # from sklearn.metrics import mean_squared_error
    # from sklearn.metrics import mean_absolute_error
    # import matplotlib.pyplot as plt
    # y_pre = model.predict(X_train)
    # # MSE
    # mse_predict = mean_squared_error(Y_trian, y_pre)
    # # MAE
    # mae_predict = mean_absolute_error(Y_trian, y_pre)
    #
    # print('mse_predict: ',mse_predict)
    # print('mae_predict: ',mae_predict)
    #
    # plt.scatter(X_train,Y_trian)
    # plt.plot(X_train,y_pre,'r-')
    # plt.legend()
    # plt.show()

    return model,pre

def model_train_piple(data,suggest_people):
    '''
    :param data: 模型训练数据集，包含index_slide,count_list,index_after_time,part_one--->时间序列下标，时间序列总打卡数，下一个时刻的下标，建议游玩时间前半段打卡数。所谓前半段时间是指（前半段时间+未来预测时间=建议游玩时间）
    :param suggest_people: 建议游玩人数
    :return:
    '''
    import numpy as np
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn import linear_model
    import matplotlib.pyplot as plt


    X_train,Y_trian = data[0],data[1]

    """ 标准误差 """

    def stdError_func(y_test, y):
        return np.sqrt(np.mean((y_test - y) ** 2))

    def R2_1_func(y_test, y):
        return 1 - ((y_test - y) ** 2).sum() / ((y.mean() - y) ** 2).sum()

    def R2_2_func(y_test, y):
        y_mean = np.array(y)
        y_mean[:] = y.mean()
        return 1 - stdError_func(y_test, y) / stdError_func(y_mean, y)



    x = np.array((X_train), dtype=float)
    y = np.array(Y_trian)

    plt.scatter(x, y, s=10, color='black', alpha=0.9)
    degrees = [7, 8, 9, 10, 11]
    # degrees =[i for i in range(2,50,5)]

    for degree in degrees:
        model = Pipeline([('poly', PolynomialFeatures(degree=degree)),
                        ('linear', linear_model.LinearRegression(fit_intercept=False, normalize=True))])

        model.fit(x[:, np.newaxis], y)  ## 自变量需要二维数组
        predict_y = model.predict(x[:, np.newaxis])
        strError = stdError_func(predict_y, y)
        R2_1 = R2_1_func(predict_y, y)
        R2_2 = R2_2_func(predict_y, y)
        score = model.score(x[:, np.newaxis], y)  ##sklearn中自带的模型评估，与R2_1逻辑相同

        print('degree={}: strError={:.2f}, R2_1={:.2f},  R2_2={:.2f}, clf.score={:.2f}'.format(
            degree, strError, R2_1, R2_2, score))

        plt.plot(x, predict_y, linewidth=2, label=degree)

    plt.legend()
    plt.show()

    # model = LinearRegression()
    # model.fit(X_train, Y_trian)
    X_pre=data[2]
    #
    X_pre = np.array((X_pre), dtype=float)
    pre=model.predict([[X_pre]])
    print('LR预测下一个十分钟：',ceil(pre))

    if ceil(pre)+data[3]>int(suggest_people):
        print('都别再来了，人可多了，都{}人了'.format(ceil(pre)+data[3]))
    else:
        print('没事，可劲打卡，只有{}人'.format(ceil(pre)+data[3]))
    #
    # # 评估
    # from sklearn.metrics import mean_squared_error
    # from sklearn.metrics import mean_absolute_error
    # import matplotlib.pyplot as plt
    # y_pre = model.predict(X_train)
    # # MSE
    # mse_predict = mean_squared_error(Y_trian, y_pre)
    # # MAE
    # mae_predict = mean_absolute_error(Y_trian, y_pre)
    #
    # print('mse_predict: ',mse_predict)
    # print('mae_predict: ',mae_predict)
    #
    # plt.scatter(X_train,Y_trian)
    # plt.plot(X_train,y_pre,'r-')
    # plt.show()

    return model,pre


def model_train_dt(data, suggest_people):
    '''
    :param data: 模型训练数据集，包含index_slide,count_list,index_after_time,part_one--->时间序列下标，时间序列总打卡数，下一个时刻的下标，建议游玩时间前半段打卡数。所谓前半段时间是指（前半段时间+未来预测时间=建议游玩时间）
    :param suggest_people: 建议游玩人数
    :return:
    '''


    X_train, Y_train = data[0], data[1]

    x = np.array(X_train,dtype=float)

    y = np.array(Y_train)

    plt.scatter(x, y, s=10, color='black', alpha=0.8)
    degrees = [13]

    for degree in degrees:
        model = Pipeline([('poly', PolynomialFeatures(degree=degree)),
                          ('linear', tree.DecisionTreeRegressor(criterion='mse'
                                                                ,random_state=50
                                                                ,splitter='random'
                                                                ,max_depth=10 #最大深度，对于高纬度，样本量少，有奇效
                                                                ,min_samples_leaf=5 #每个节点至少拥有的样本数
                                                                ,min_samples_split=10 #每个非叶子结点至少拥有样本数

                                                                ))])

        model.fit(x[:, np.newaxis], y)  # 自变量需要二维数组

        predict_y = model.predict(x[:, np.newaxis])
        plt.plot(x, predict_y, linewidth=2, label=degree)

    X_pre = data[2]
    pre = model.predict([[X_pre[0]]])
    plt.legend()
    plt.show()

    return model, pre
def slide_windows(formId,data,today,after_time,open_time, close_time,time_distance,suggest_time,step):

    '''
    :param data: 数据集
    :param today: 今日时间
    :param after_time: 10分钟后具体时间
    :param open_time: 开馆时间
    :param close_time: 闭馆时间
    :param time_distance: 时间跨度
    :param suggest_time: 建议游玩时间
    :param step  滑动一次的距离
    :return:
    '''

    '''
    设置一个长度为 time_distance 的滑动窗口  slide_windows.
    将时间在 open_time 和 close_time 之间的时间细化到分钟，组成一个时间序列.
    用滑动窗口slide_windows 在时间序列上滑动，得到一个个的窗口大小的序列.
    将窗口序列视为一个整体，统计该时间序列内，游客总数，得到一个 时间序列 与 时间序列内游客总数 的数据集，作为训练数据集。
    '''

    if step>time_distance:
        print('请设置合理的step,step大于时间跨度，将有时间段无法预测：正在退出程序。。。。')
        print('请修改step或time_distance值,确保step不大于time_distance')
        os._exit(0)

    # 根据场馆id区分出各个场馆数据
    data = data[data['formId'].isin([formId])]


    #游玩时间 = [sugess2begin,sugess2now]+[10未来十分钟]
    if int(suggest_time)>time_distance:

        sugess2begin = today+datetime.timedelta(minutes=-(int(suggest_time)-int(time_distance))) #当前时间的建议游玩时长，比如建议游玩半小时，此处计算的是  前20分钟~当前时间 段。（目的是加上预测10分钟时间，得到完成的建议游玩时间）

        sugess2begin = str(sugess2begin)[:-9]+'00' # 2020-05-27 09:56:08.077629 ----->>>>>>  2020-05-27 09:56:00
        sugess2now = str(today)[:-9]+'00'  #当前时间 2020-05-27 10:25:00

        tiem_id_punch_sugess = data.loc[lambda df: (df['createTime'] <= sugess2now) & (df['createTime'] >=sugess2begin), :]

        # [sugess2begin,sugess2now] 中的打卡数
        part_one = sum(list(tiem_id_punch_sugess['num']))
        print('建议游玩时间区间第一部分：开始{},中点{},结束{}, 当前时间内打卡人数为：{} '.format(sugess2begin,sugess2now,after_time,part_one))
    else:
        part_one = 0  #如果建议游玩时间，小于预测区间，则默认在下一个区间到来之前，游客离开了
        print('建议游玩时间较短，没有跨区间计算，故默认为游客离开，遗留游客为0')


    # 时间序列
    today_ = datetime.datetime.strftime(today, '%Y-%m-%d')
    # beforeday=str(date_transor(today_,7)) #以{1}天内数据做为数据集

    # 将时间以分钟切开
    df =[]
    days =7 #以{7}天内数据做为数据集
    for i in range(days+1):
        rang_date = pd.date_range(start=str(date_transor(today_,days-i)) + ' ' + open_time, end=str(date_transor(today_,days-i)) + ' ' + close_time, freq='min')
        df.extend(rang_date)

    rang_date=df

    list_rang_date =[]


    after_time = pd.date_range(start=after_time, end=after_time , freq='min')
    after_time_ =[]
    after_time_.extend(after_time)

    # 滑动方式2
    # step = 1  #两次滑动的跨度（必须大于1）
    pivote = 0 #初始化滑动起始点
    after_time_index_list = []
    for i in range(0,len(rang_date)-time_distance+1):
       list_rang_date.append(rang_date[pivote:pivote+time_distance])
       pivote += step

       if after_time_[0] in rang_date[pivote:pivote+time_distance]:
           after_time_index_list.append(len(list_rang_date)+1)
       if pivote > len(rang_date)-time_distance+1:
            break

    index_after_time =after_time_index_list[0]
    print(after_time_index_list)

    index_slide = [i for i in range(1, len(list_rang_date) + 1)]  # 时间序列下标

    count_list=[] #对应时间序列下，打卡数量

    for time in list_rang_date:
        count = 0 #用于计算每个窗口中打卡数量

        if str(time[0])<=str(today):
            for t in time:
                if str(t) in list(data['createTime']):
                    index = list(data['createTime']).index(str(t))
                    count+=list(data['num'])[index]
            count_list.append(count)

    index_slide=index_slide[0:len(count_list)]
    # X,Y,需要预测的时刻X,建议游玩区间前半部分打卡数
    # 返回值为，时间下标，下标下统计人数，下一个时间下标未来，建议游玩时间的前半段总人数
    return index_slide,count_list,after_time_index_list,part_one




if __name__ == '__main__':

    # 参数
    oprn_time = '06:30:00'
    close_time = '18:00:00'
    suggest_time='35'
    time_distance = 30
    suggest_people=20

    # 时间部分
    dateTime_s = time.time()  # 获取当前时间戳

    dateTime_s = datetime.datetime.fromtimestamp(dateTime_s)  # 将时间戳转换为日期

    after_time = dateTime_s + datetime.timedelta(minutes=+time_distance)
    after_time = datetime.datetime.strftime(after_time, '%Y-%m-%d %H:%M:%S')


    after_time = after_time[0:-2] + '00'
    print('{}分钟之后是：{}'.format(time_distance,after_time))

    # 日志
    logging.basicConfig(level=logging.ERROR,  # 控制台打印的日志级别
                        filename='人流预警.log'+'-----'+' dateTime_s',
                        filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                        # a是追加模式，默认如果不写的话，就是追加模式
                        format=
                        '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                        # 日志格式
                        )




    try:
        #获取数据
        myclient = MongoClient("mongodb://10.200.4.92:0000/")  # 端口信息
        mydb = myclient["oasis"]  # 库
        mydb.authenticate('oasis', '123456')  # 权限认证，用户名密码
        hymUserPunch = mydb["hymUserPunch"]  # 打卡表
        punch = pd.DataFrame(list(hymUserPunch.find()))
        tiem_id_punch = punch[['userId', 'formId', 'createTime']]

        one = [1 for i in range(0, len(tiem_id_punch))]
        tiem_id_punch['num'] = one
        tiem_id_punch = tiem_id_punch[tiem_id_punch['formId'] >= '1']
    except:
         logging.error('数据加载出错')
         email('数据加载出错')


    # example:
    # userId                    formId           createTime  num
    # 4317  5e9eb4fdc461ae4981d74407  2020-03-27 12:26:00    1
    # 4317  5e9eb4fdc461ae4981d74407  2020-03-28 12:26:00    1
    # 4317  5e9eb4fdc461ae4981d74407  2020-03-29 12:26:00    1


    # 用假数据训练一下看看效果
    # tiem_id_punch=faker_data()
    tiem_id_punch = pd.read_csv('data_faker')

    # 假数据截至此


    try:
        tiem_id_punch['createTime'] = tiem_id_punch['createTime'].map(lambda x: str(x)[0:16] + ':00')

        # 场馆id列表
        form_tel = tiem_id_punch[['tel','formId']].drop_duplicates(keep='first')
        # print(form_tel)
        form_tel = form_tel.to_dict(orient='records')
    except:
        logging.error('数据预处理出错')
        email('数据预处理出错')


    url = "http://10.200.3.51:6031/member-api/message/send"




    if after_time >= str(dateTime_s)[0:10] + ' ' + close_time:
        print('闭馆啦,明日再来吧')
    else:
        print('没事，还可以浪')

        for i in form_tel:
            try:
                formId = i['formId']
                tel = i['tel']
            except:
                logging.error('没有找到电话和场馆id字段')
                email('没有找到电话和场馆id字段')
                break
            payload = {
                        'params': [{}],
                        "phone": tel,
                        "templateCode": "jymklyjtzh"
                      }

            print('***************************')
            print('当前场馆是：{}  ,联系方式是：{}'.format(formId,tel))
            for s in [15]:
                try:
                    data =slide_windows(formId,tiem_id_punch,dateTime_s,after_time,oprn_time,close_time,time_distance,suggest_time,step=s)
                except:
                    logging.error('slide_windows error')
                    email('slide_windows error')
                    break

                try:
                    model , pre = model_train_dt(data,suggest_people=20)
                except:
                    logging.error('model trianning error')
                    email('model trianning error')

                print('LR预测下一个{}分钟：{}'.format(time_distance,ceil(pre)))

                if ceil(pre) + data[3] > int(suggest_people):
                    print('都别再来了，人可多了，都{}人了'.format(ceil(pre) + data[3]))

                    short_message = requests.post(url, json=payload)  # json 参数直接自动传 json

                else:
                    print('没事，可劲打卡，只有{}人'.format(ceil(pre) + data[3]))
