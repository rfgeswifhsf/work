import random
import timeit
import time
import datetime


# 计算今天和一个日期的天数差值
def time_mul(time_str):
    '''
    :param time_str: 字符串时间
    :return: 返回字符串时间 time_str 所表示的时间与当前时间的时间差。
    '''
    now_str = datetime.datetime.now().strftime('%Y-%m-%d')
    now = datetime.datetime.strptime(now_str, "%Y-%m-%d")
    future = datetime.datetime.strptime("2019-12-01", "%Y-%m-%d")
    days = (future - now).days
    return days

# 该函数随机生成未来一个月内的日期
def generatorDatetime(num=7):
    '''
    一个月内的随机时间
    :return:
    '''
    dateTime_s = time.time()  # 获取当前时间戳
    dateTime_s = datetime.datetime.fromtimestamp(dateTime_s)  # 将时间戳转换为日期
    str_p = datetime.datetime.strftime(dateTime_s, '%Y-%m-%d %H:%M:%S')  # 将日期转换为字符串
    str_p = dateTime_s + datetime.timedelta(minutes= - 10)  # 当前时间的建议游玩时长，比如建议游玩半小时，此处计算的是  前20分钟~当前时间 段。（目的是加上预测10分钟时间，得到完成的建议游玩时间）
    str_p = datetime.datetime.strftime(str_p, '%Y-%m-%d %H:%M:%S.%f')

    # 当前日期加-7天
    month = datetime.timedelta(days=-num)

    dateTime_end = dateTime_s + month

    dateTime_end = datetime.datetime.strftime(dateTime_end, '%Y-%m-%d %H:%M:%S')  # 将日期转换为字符串

    # 将字符串转换为时间戳
    dateTime_s_stamp = time.mktime(time.strptime(str_p, '%Y-%m-%d %H:%M:%S.%f'))
    dateTime_e_stamp = time.mktime(time.strptime(dateTime_end, '%Y-%m-%d %H:%M:%S'))

    t = random.randint(dateTime_e_stamp,dateTime_s_stamp)
    date_touple = time.localtime(t)  # 将时间戳生成时间元组
    date = time.strftime("%Y-%m-%d %H:%M:%S", date_touple)  # 将时间元组转成格式化字符串（1976-05-21）
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    return date



# print(generatorDatetime())
