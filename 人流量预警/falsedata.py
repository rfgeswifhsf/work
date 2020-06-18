import datetime
import random
import pandas as pd
from  date_rand import generatorDatetime

def randomtimes(start, end, n, frmt="%Y-%m-%d"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    return [random.random() * (etime - stime) + stime for _ in range(n)]

def faker_data():
    userId = [ i for i in range(0,1000)]
    formId = [random.randint(4211,4212) for i in range(0,1000)]
    createTime = [generatorDatetime() for i in range(0,1000)]
    num=[1 for i in range(0,1000)]
    tel =['15623819250' for i in range(0,1000)]

    df = pd.DataFrame([userId,formId,createTime,num,tel],index=['userid','formId','createTime','num','tel'])

    return df.T

a = faker_data()
# print(a)
a.to_csv("data_faker")

