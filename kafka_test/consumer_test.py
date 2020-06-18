import json
from json import loads

from kafka import KafkaConsumer

# group_id,是为了不影响其他应用对同一kafka topic的消费，自己随便取名字，但是不能重名
# auto_offset_reset='latest' 表示从最新位置开始消费，earliest表示最早位置
consumer = KafkaConsumer("zhangwei123", bootstrap_servers=["10.200.5.117:9092"],group_id='wm_group',auto_offset_reset='latest')
print('begin')
for msg in consumer:
    print('1')
    # print(msg.value)
    a=json.loads(s=msg.value)
    print(a['data'])


