"""
    常用的方法
"""
import datetime
import json
import random
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
from html.parser import HTMLParser
import os
import pymysql
import requests
from DBUtils.PooledDB import PooledDB
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
# from constant_data import ua_pool, insert_info_image_url, insert_info_deal_img_detail, upload_url, insert_info_tag_list, insert_info_relation_tag_content
# from sql import insert_info_url_list, insert_info_detail, insert_info_image_url_sql, insert_info_deal_image_detail, insert_info_tag_relation
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def sub_useless_tag(txt):
    """
    有些语义化标签需要去除
    :param txt:
    :return:
    """
    replace_str = ["&#39;", "&quot;", "&nbsp;", "&gt;", "&lt;", "&yen;", "&amp;", "}", "]"]
    is_replace_str = ["'", '"', " ", ">", "<", "￥", "&", "", ""]
    for index, _ in enumerate(replace_str):
        txt = txt.replace(_, is_replace_str[index])
    if "&#39;" in txt:
        txt = txt.replace("&#39;", "'")
    return txt


def cancel_useless_tag(txt):
    """
    有些语义化标签需要去除
    :param txt:
    :return:
    """
    replace_str = ["&#39;", "'", "&quot;", '"', "&nbsp;", " ", "&gt;", ">", "&lt;", "<", "&yen;", "￥", "&amp;", "&",
                   "}", "]"]

    for _ in replace_str:
        txt = txt.replace(_, "")

    return txt


def cancel_txt(txt):
    """
    传入文章的title中可能含有一些语义的文本例如：&gt;;\n等，替换或者转换
    :param txt:
    :return:
    """
    unescape_txt = HTMLParser().unescape(txt)

    return unescape_txt


def get_yesterday():
    """
    获取昨天的日期
    :return:
    """
    yesterday = datetime.date.today() + datetime.timedelta(-1)

    return yesterday


def get_today():
    """
    获取当前日期
    :return:
    """
    today = datetime.date.today()

    return today


def get_now_datetime():
    """
    获取当前日期和时间
    :return:
    """
    now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    return now_datetime


def get_yesterday_str():
    """
    获取到前一天的00:00:00
    :return:
    """
    _yesterday = get_yesterday()
    yesterday_str = datetime.datetime.strptime(_yesterday.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return yesterday_str


def today_str():
    """
    获取今天的00:00:00
    :return:
    """
    _today_str = get_today()
    today_str = datetime.datetime.strptime(_today_str.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return today_str


class Response(object):
    """
    构造一个响应类,对于请求失败的返回的值
    """

    def __init__(self, url):
        self.status_code = 999
        self.content = ""
        self.url = url
        self.text = {}


def req_res(url=None, headers=None, params=None, data=None, proxies=None, timeout=6, method="GET"):
    """
    请求参数,获取响应,返回响应
    :param url:
    :param headers:
    :param params:
    :param data:
    :param proxies:
    :param timeout:
    :param method:
    :return:
    """
    response = Response(url)
    try:
        if method == "GET":
            response = requests.get(url=url, headers=headers, params=params,
                                    proxies=proxies, verify=False,
                                    allow_redirects=False, timeout=timeout)
        else:
            response = requests.post(url=url, headers=headers, data=data,
                                     proxies=proxies, verify=False,
                                     allow_redirects=False, timeout=timeout)
    except Exception as e:

        pass
    finally:
        return response


def get_feiyi():
    """
    飞蚁代理试用
    :return:
    """
    three_min_url = "http://183.129.244.16:88/open?user_name=fengyewangap1&timestamp=1569379659&md5=5CBFAF2F90F7EB06D1F22F424E76FD44&pattern=json&number=1"
    five_min_url = "http://183.129.244.16:88/open?user_name=fengyewangap3&timestamp=1569285644&md5=858FA65184F5E8F7064165082672EA92&pattern=json&number=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    response = Response(three_min_url)
    for _ in range(3):
        try:
            response = requests.get(three_min_url, headers=headers, verify=False, timeout=3)
            if response.status_code == 200:
                break
        except Exception as exc:
            continue
    json_data = json.loads(response.content.decode())
    if json_data:
        port = json_data.get('port')[0]
        ip = json_data.get('domain')
        str_ip_port = "{}:{}".format(ip, port)
        proxy_str = dict()
        proxy_str = {"https": 'http://{}'.format(str_ip_port), "http": 'http://{}'.format(str_ip_port)}
        return proxy_str
    else:
        print("未获取到IP值")


def upload_data_pro(env, img_dict=None, tmp_dict=None, tag_relation_data=None):
    """
    同步到三个环境的方法
    :param env:  环境的ip 和域名
    :param img_dict:  图片的数据
    :param tmp_dict: 清新完的数据
    :return:
    """
    headers = {"User-Agent": random.choice(ua_pool)}
    img_res = None
    detail_res = None
    tag_res = None
    if tag_relation_data is not None:
        # 标签关联表数据插入到对应环境的表中
        tag_dict = dict()
        tag_dict.setdefault('newsId', tag_relation_data.get('news_id'))
        tag_dict.setdefault('tagsId', tag_relation_data.get('tags_id'))
        tag_res = req_res(url=insert_info_relation_tag_content.format(env), headers=headers,
                          data=tag_dict, timeout=3, method="POST")
    if img_dict is not None:
        img_dict_env = dict()
        img_dict_env['imgUrl'] = img_dict.get('img_url')
        img_dict_env['detailNewsId'] = img_dict.get('detail_news_id')
        # 标题图数据插入到对应环境的表中
        img_res = req_res(url=insert_info_image_url.format(env), headers=headers,
                          data=img_dict_env, timeout=3, method="POST")
    if tmp_dict is not None:
        clean_detail_env = dict()
        clean_detail_env['clickNumber'] = tmp_dict.get('click_number')
        clean_detail_env['newsType'] = tmp_dict.get('news_type')
        clean_detail_env['source'] = tmp_dict.get('source')
        clean_detail_env['title'] = tmp_dict.get('title')
        clean_detail_env['author'] = tmp_dict.get('author')
        clean_detail_env['releaseDate'] = tmp_dict.get('release_date')
        clean_detail_env['urlListId'] = tmp_dict.get('url_list_id')
        clean_detail_env['content'] = tmp_dict.get('content')
        clean_detail_env['restr'] = tmp_dict.get('restr')
        clean_detail_env['isDelete'] = tmp_dict.get('is_delete')
        clean_detail_env['authorIconUrl'] = tmp_dict.get('author_icon_url')
        clean_detail_env['url'] = tmp_dict.get('url')
        clean_detail_env['originalDetailId'] = tmp_dict.get('id')
        clean_detail_env['category'] = tmp_dict.get('category')
        clean_detail_env['station'] = tmp_dict.get('station')
        # 清洗完成数据插入到对应环境的表中
        detail_res = req_res(url=insert_info_deal_img_detail.format(env), headers=headers,
                             data=clean_detail_env, timeout=3, method="POST")

    return img_res, detail_res, tag_res


def insert_mysql_data(logger, _conn, _cursor, tmp_url_list=None, tmp_detail=None, tmp_deal_image_detail=None,
                      tmp_img_dict=None, tmp_relation_tag=None):
    """
    插入数据方法
    :param _conn: 日志操作对象
    :param _conn: 数据库对象
    :param _cur:  游标
    :param tmp_url_list: 插入列表页的字典数据
    :param tmp_detail:  插入详情页的字典数据
    :param tmp_deal_image_detail:  插入清洗表的字典数据
    :param tmp_img_dict:  插入图片表的字典数据
    :return:
    """
    flag = False
    if tmp_url_list is not None:
        # 将数据插入到url列表表中..
        try:
            _cursor.execute(insert_info_url_list, (tmp_url_list.get('category'),
                                                   tmp_url_list.get('url'),
                                                   tmp_url_list.get('web_name'),
                                                   tmp_url_list.get('title'),
                                                   tmp_url_list.get('create_time'),
                                                   tmp_url_list.get('is_upload'),
                                                   ))
            _conn.commit()
            flag = True
        except Exception as exc:
            _conn.rollback()
            logger.error("执行插入列表页sql失败．．．．．．{}".format(exc))
    elif tmp_detail is not None:
        # 将数据插入到详情表
        try:
            _cursor.execute(insert_info_detail, (tmp_detail.get('click_number'),
                                                 tmp_detail.get('news_type'),
                                                 tmp_detail.get('source'),
                                                 tmp_detail.get('title'),
                                                 tmp_detail.get('author'),
                                                 tmp_detail.get('release_date'),
                                                 tmp_detail.get('url_list_id'),
                                                 tmp_detail.get('content'),
                                                 tmp_detail.get('create_time'),
                                                 tmp_detail.get('author_icon_url'),
                                                 tmp_detail.get('is_upload'),
                                                 tmp_detail.get('station')))
            _conn.commit()
            flag = True
        except Exception as exc:
            logger.error("插入详情页sql失败．．．．．{}".format(exc))
            _conn.rollback()

    elif tmp_img_dict is not None:
        # 将数据插入到标题图表
        try:
            _cursor.execute(insert_info_image_url_sql, (tmp_img_dict.get('img_url'),
                                                        tmp_img_dict.get('detail_news_id'),
                                                        tmp_img_dict.get('create_time'),
                                                        tmp_img_dict.get('is_upload'),))
            _conn.commit()
            flag = True
        except Exception as exc:
            logger.info("插入到图片的标题图失败{}".format(exc))
            _conn.rollback()

    elif tmp_relation_tag is not None:
        # 将数据插入到标签关联表
        try:
            _cursor.execute(insert_info_tag_relation, (tmp_relation_tag.get('news_id'),
                                                        tmp_relation_tag.get('tags_id'),
                                                        tmp_relation_tag.get('create_time'),
                                                        ))
            _conn.commit()
            flag = True
        except Exception as exc:
            logger.info("插入到图片的标题图失败{}".format(exc))
            _conn.rollback()

    elif tmp_deal_image_detail is not None:
        # 将数据插入到清洗表
        try:
            _cursor.execute(insert_info_deal_image_detail, (tmp_deal_image_detail.get('click_number'),
                                                            tmp_deal_image_detail.get('news_type'),
                                                            tmp_deal_image_detail.get('source'),
                                                            tmp_deal_image_detail.get('title'),
                                                            tmp_deal_image_detail.get('author'),
                                                            tmp_deal_image_detail.get('release_date'),
                                                            tmp_deal_image_detail.get('url_list_id'),
                                                            tmp_deal_image_detail.get('content'),
                                                            tmp_deal_image_detail.get('create_time'),
                                                            tmp_deal_image_detail.get('restr'),
                                                            tmp_deal_image_detail.get('is_delete'),
                                                            tmp_deal_image_detail.get('author_icon_url'),
                                                            tmp_deal_image_detail.get('url'),
                                                            tmp_deal_image_detail.get('id'),
                                                            tmp_deal_image_detail.get('category'),
                                                            tmp_deal_image_detail.get('is_upload'),
                                                            tmp_deal_image_detail.get('station'),
                                                            ))
            _conn.commit()
            flag = True
        except Exception as e:
            _conn.rollback()
            logger.error("插入失败{}".format(e))

    return _conn, _cursor, flag


def req_pic(img_url):
    """
    获取图片内容
    :param url:
    :return:
    """
    response = req_res(url=img_url[0], headers={"user-agent": random.choice(ua_pool)})
    return response


def request_img_translate_our(img_list):
    """
    获取图片的连接，请求下来，然后上传到我们公司图片服务器
    :param img_list:
    :return:
    """
    image_name_dict = dict()
    with ThreadPoolExecutor(5) as executor:
        all_task = [executor.submit(req_pic, (url,)) for url in img_list]
        wait(all_task, return_when=ALL_COMPLETED)
        for future in as_completed(all_task):
            if future.result().status_code == 200:
                # image_name_dict[future.result().url] = future.result().content
                timestatmp = str(int(time.time() * 1000))
                # 生成图片的对象载体,接口才能识别
                file_name = "{}".format(os.getpid()) + 'first{}.jpg'.format(
                    timestatmp)
                tiple_tmp = ('file', (file_name, future.result().content, 'image/png'))
                tmp_data_list = list()
                tmp_data_list.append(tiple_tmp)
                try:
                    upload_response = requests.post(url=upload_url,
                                                    headers={"user-agent": random.choice(ua_pool)},
                                                    files=tmp_data_list, verify=False, timeout=5)
                    if json.loads(upload_response.text).get('success'):
                        upload_img_url = json.loads(upload_response.text).get('data')[0].get('url')
                        image_name_dict[future.result().url] = upload_img_url
                    else:
                        # 上传失败，将原ＵＲＬ的值设置为空字符串
                        image_name_dict[future.result().url] = ""
                except Exception as e:
                    image_name_dict[future.result().url] = ""
            else:
                """当前图片的请求失败后，后续直接将这个ＵＲＬ置换为空"""
                image_name_dict[future.result().url] = ""

    return image_name_dict


def get_db(host=None, user=None, port=None, password=None, db=None, charset=None):
    """
    # 线程池链接数据库,生成数据库连接池
    :param host: 数据库ip值
    :param user: 用户名
    :param port:  端口
    :param password: 密码
    :param db:   数据库对象
    :param charset:  字符集对象
    :return:  数据库对象
    """
    max_connections = 15
    pool_mysql = PooledDB(pymysql,
                          max_connections,
                          host=host,
                          user=user,
                          port=port,
                          passwd=password,
                          db=db,
                          use_unicode=True,
                          charset=charset
                          )
    return pool_mysql


ua_pool = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
]

from skimage import io
import requests
import pymysql
import pandas as pd
from sqlalchemy import create_engine
from pprint import pprint


engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')
sql = '''select * from countyside;'''
df = pd.read_sql_query(sql, engine)
# 输出employee表的查询结果


# 上传图片的接口地址
upload_url = "https://mind.lvmama.com/ms-api/upload/uploadPic"

urls=['http://183.201.254.66:9000/shanxi//2019/3/26/commerce/95fb7499652d460cb8042050318c3a3f.jpg','http://183.201.254.66:9000/shanxi//2019/6/27/commerce/23126a028b72459daaf502f9dbbe8eb1.png']
r=request_img_translate_our(df['imageurl'].tolist())
df_url = pd.DataFrame(r,index=['0'])
df_url_new = df_url.T
# print(df_url_new['0'])

list_url=[]
for i in df['imageurl']:
    list_url.append(df_url_new['0'][i])
df['img_url']=list_url
print(df['img_url'])
df['dest_type']=['counttyside' for i in range(len(df))]
df['dest_type_name']=['3A级示范村' for i in range(len(df))]
del df['imageurl']


# // 将腾讯 / 高德地图经纬度转换为百度地图经纬度
# function
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
a,b=qqMapTransBMap(112.665866,38.107789)
print(a,b)


engine = create_engine('mysql+pymysql://root:111111@192.168.0.63:3306/afanti?charset=utf8',encoding='utf-8')
df.to_sql('dest_countyside',engine,if_exists='replace',index=False)
