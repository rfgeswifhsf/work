# -*- coding:utf8 -*-
import smtplib
from email.mime.text import MIMEText
def email(content="邮件内容，我是邮件内容，哈哈哈"):
    msg_from = '990250040@qq.com'  # 发送方邮箱
    passwd = 'sijqyfqqghoxbbdb'  # 填入发送方邮箱的授权码(填入自己的授权码，相当于邮箱密码)
    msg_to = ['zhangwei1@lvmama.com']  # 收件人邮箱
    subject = "人流量预警ERROR"  # 主题
    content = content
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
