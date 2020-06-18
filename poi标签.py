import pandas as pd
from sqlalchemy import create_engine, VARCHAR

engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')
sql_view = '''select distinct scenic_tag from ysx_view_hotel_poi where dest_type_name = '景点';'''
sql_hotel = '''select distinct tag from t_hotel_detail ;'''
sql_ysh_poi = '''SELECT baidutag,new_type from ysx_poi  where new_type!='酒店' and new_type!='景点' GROUP BY (baidutag) ;'''

df_view = pd.read_sql_query(sql_view, engine)

df_hotel = pd.read_sql_query(sql_hotel, engine)

df_ysh_poi = pd.read_sql_query(sql_ysh_poi, engine)


df_tag= pd.DataFrame(data=None,columns=['tag_id','tag_name','dest_type','dest_type_name','tag_parent_id','tag_parent'])
#
i=1
#
tag_name_list=[]
dest_type=[]
dest_type_name=[]
# for tags in df_view['scenic_tag'] :
#     try:
#         for tag  in tags.split(','):
#             if tag not in tag_name_list and tag!='':
#                 i+=1
#                 tag_name_list.append(tag)
#                 dest_type.append('VIEWSPOT')
#                 dest_type_name.append('景点')
#     except:
#         print('?')
#
# '''多定一个是不想让 不同type_nema但是tag相同的被过滤掉'''
# tag_name_list_=[]
# for tags in df_hotel['tag'] :
#     try:
#         for tag  in tags.split(','):
#             if tag not  in tag_name_list_ and tag !='':
#                 tag_name_list_.append(tag)
#                 dest_type.append('HOTEL')
#                 dest_type_name.append('酒店')
#     except:
#         print(tags)
#
# tag_name_list.extend(tag_name_list_)
# print(len(tag_name_list))
# df_tag['tag_name']=tag_name_list
# df_tag['dest_type']=dest_type
# df_tag['dest_type_name']=dest_type_name
# tag_id=[i for i in range(1,len(tag_name_list)+1)]
# df_tag['tag_id']=tag_id



for m,tags in enumerate(df_ysh_poi['baidutag']) :
    try:
        if tags not in tag_name_list and tags!='':
            i+=1
            tag_name_list.append(tags)
            # dest_type.append('')
            dest_type_name.append(df_ysh_poi['new_type'][m])
    except:
        print('?')

df_tag['tag_name']=tag_name_list
# df_tag['dest_type']=dest_type
df_tag['dest_type_name']=dest_type_name
tag_id=[i for i in range(141,len(tag_name_list)+1+140)]
# df_tag['tag_id']=tag_id
print(df_tag)

type_dict={'tag_name':VARCHAR(50),'dest_type':VARCHAR(50),'dest_type_name':VARCHAR(50),'tag_parent_id':VARCHAR(50),'tag_parent':VARCHAR(50)}
# df_tag.to_sql('tag_poi_copy1',engine,if_exists='append',index=False)
conn = engine.connect()
df_tag.to_sql('tag_poi',engine,if_exists='append',index=False,dtype=type_dict)
# conn.execute('''alter table tag_poi_copy2 add primary key(tag_id); ''')
# conn.execute(f"-- alter table tag_poi_copy2 change tag_id tag_id int AUTO_INCREMENT")
