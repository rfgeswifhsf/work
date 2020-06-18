import json
import time
from kafka import KafkaProducer
from pprint import pprint
import pandas as pd
from canal.client import Client
from canal.protocol import EntryProtocol_pb2

client = Client()
client.connect(host='10.200.5.117', port=11111)
client.check_valid(username=b'maxwell', password=b'123456')

database=b'afanti.canal_test'
# database=b'maxwell.test'

client.subscribe(client_id=b'1001', destination=b'example', filter=b'afanti.rec_useraction')

while True:
    message = client.get(100)
    # print(message)
    entries = message['entries']
    format_data = dict()
    for entry in entries:
        entry_type = entry.entryType
        # if entry_type in [EntryProtocol_pb2.EntryType.TRANSACTIONBEGIN, EntryProtocol_pb2.EntryType.TRANSACTIONEND]:
        #     continue

        row_change = EntryProtocol_pb2.RowChange()

        row_change.MergeFromString(entry.storeValue)
        event_type = row_change.eventType
        header = entry.header
        database = header.schemaName
        table = header.tableName
        event_type = header.eventType

        for row in row_change.rowDatas:
            if event_type == EntryProtocol_pb2.EventType.DELETE:
                for column in row.beforeColumns:
                    format_data[ column.name]=column.value

            elif event_type == EntryProtocol_pb2.EventType.INSERT:
                for column in row.afterColumns:

                    format_data[column.name] = column.value

            elif event_type == EntryProtocol_pb2.EventType.UPDATE:
                for column in row.afterColumns:
                    format_data[column.name] = column.value
            else:
                format_data['before'] = format_data['after'] = dict()
                for column in row.beforeColumns:
                    format_data['before'][column.name] = column.value
                for column in row.afterColumns:
                    format_data['after'][column.name] = column.value
            data = dict(
                db=database,
                table=table,
                event_type=event_type,
                data=format_data,
            )
            # print('********************'*5)
            # print('********************'*5)
            # print(data)
            # print('********************'*5)
            # print('********************'*5)
            producer = KafkaProducer(bootstrap_servers=["10.200.5.117:9092"])
            msg = json.dumps(data)
            print(msg)
            producer.send('zhangwei1', value=msg.encode('utf-8'))
    time.sleep(1)







client.disconnect()


