import re
from pprint import pprint
import pandas as pd
from sqlalchemy import create_engine


'''
# e1.product_id,e1.user_id ,t1.product_name,t1.dest_id,t1.goods_name,t1.dest_type,t1.dest_name,t1.district_name,t1.district_id
'''
# column=['product_id','user_id','product_name','dest_id','goods_name','dest_type','dest_name','district_name','district_id']



df = pd.DataFrame(columns=['product_id','user_id','product_name','dest_id','goods_name','dest_type','dest_name','district_name','district_id'])
df1=open('zgv.udm',encoding='ANSI').readlines()
print(len(df1))
# df= pd.DataFrame()
# df1= open('zzd',encoding='utf-8').readlines()
# print(len(df1))
productID_list=[]
for i in range(0,len(df1)-1):
        if i%100==0:
            print(i)
        if i%2==0:
            df1[i]=df1[i].strip('\n')
            df1[i+1] = df1[i+1].strip('\n')
            data1 = df1[i].split('\t')
            if 'product_id' in data1 :
                data1=[j for j in data1 if len(j)!=0]
                data2 = df1[i+1].split('\t')
                if data2[data1.index('product_id')] not in productID_list:
                    productID_list.append(data2[data1.index('product_id')])
                    data2=[j for j in data2 if len(j)!=0]

            # print(data1)
            # print(data2)
            # l=zip(data1,data2)
            # L.append(list(l))

                    df_ = pd.DataFrame(data2,index=data1)
                    # print(df_.T)
                    # try:
                    df=df.append(df_.T)
                    # except:
            #     print(i)
            #     print(df_.T)
# pprint(L)


engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')
#
df.to_sql('t_test_app1',engine,if_exists='replace',index=False)
print('finish')


