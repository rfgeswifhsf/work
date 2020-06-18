# import requests
# import json
#
# payload ={
#          'params':[{}],
#          "phone": "15623819250",
#           "templateCode": "jymklyjtzh"}
#
# url = "http://10.200.3.51:6031/member-api/message/send"
#
# # 第一种直接传 json 参数（推荐使用这种）data
# r1 = requests.post(url, json=payload)  # json 参数直接自动传 json
# print(r1.status_code)
# print(r1.text)

# print("---------------------------------------")
# # 第二种传 data 参数，需要转 json
# r2 = requests.post(url, json=json.dumps(payload))  # 传 data 参数就需要传 json
# print(r2.text)


import smtplib
from email.mime.text import MIMEText

msg_from = '990250040@qq.com'  # 发送方邮箱
passwd = 'sijqyfqqghoxbbdb'  # 填入发送方邮箱的授权码(填入自己的授权码，相当于邮箱密码)
msg_to = ['zhangwei1@lvmama.com']  # 收件人邮箱
subject = "邮件标题"  # 主题
content = "邮件内容，我是邮件内容，哈哈哈"
# 生成一个MIMEText对象（还有一些其它参数）
msg = MIMEText(content)
# 放入邮件主题
msg['Subject'] = subject
msg['From'] = msg_from

# 通过ssl方式发送，服务器地址，端口
s = smtplib.SMTP_SSL("smtp.qq.com", 465)
# 登录到邮箱
s.login(msg_from, passwd)
# 发送邮件：发送方，收件方，要发送的消息
s.sendmail(msg_from, msg_to, msg.as_string())
print('成功')


