import random
import time

from sqlalchemy import create_engine

from 人流量预警 import date_rand
import pandas as pd
i=0
while True:
    # 用户列表
    userList=[i for i in range(1000,2000)]
    userId = [random.sample(userList, 1)[0] for i in range(0,1)]

    # 用户行为[点击，购买，预定，收藏,评论，分享]
    acrionlist=['click','purchase','reserve','follow','comment','share','unfollow','reschedule','chargeBack','paied']
    useraction = [random.sample(acrionlist, 1)[0] for i in range(0,1)]

    # 近一个月的用户浏览的时间
    click_time = [date_rand.generatorDatetime(30) for i in range(0,1)]

    # 用户打开到关闭时间
    open_time =[]

    # 产品列表
    prodList=[i for i in range(22222,33333)]
    proId = [random.sample(prodList, 1)[0] for i in range(0,1)]


    df = pd.DataFrame([userId,useraction,proId,click_time],index=['user_id','user_action','proid','click_time']).T
    print(df)

    engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')

    df.to_sql('rec_useraction',engine,if_exists='append',index=False)
    i+=1
    print('++++++++++++++++++++++++++++')
    time.sleep(5)
