from pymongo import MongoClient
conn = MongoClient('10.200.4.92', 40000)

db = conn.hymForm
hymForm = db.hymForm

for i in hymForm.find():
    print(i)

# for i in hymForm.find({"name": "zhangsan"}):
#     print(i)
