import math
def qqMapTransBMap(lng, lat):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0;
    x = lng;
    y = lat;
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi);
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi);
    lngs = z * math.cos(theta) + 0.0065;
    lats = z * math.sin(theta) + 0.006;
    return lngs,lats



import pandas as pd
from skimage import io
import requests
import pymysql
from sqlalchemy import create_engine
from pprint import pprint
engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')
sql = '''select * from countyside;'''
df = pd.read_sql_query(sql, engine)
df_1 = df[['name','lng','lat']][0:2]
print(df_1)

for i in range(len(df_1)):
    df_1['lng'][i],df_1['lat'][i] =qqMapTransBMap(float(df_1['lng'][i]),float(df_1['lat'][i]))

