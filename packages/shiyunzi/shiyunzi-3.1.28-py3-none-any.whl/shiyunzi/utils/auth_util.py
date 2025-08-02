from shiyunzi.PJYSDK.PJYSDK import *
import uuid
import os

pjysdk = PJYSDK(app_key='cvsbutrdqusvavn72i30', app_secret='ly9HJXA4atA1jMjH0poiAdGuAWzy0iDB')
pjysdk.debug = False

def login(card: str):
    pjysdk.set_device_id(str(uuid.uuid4()))  # 设置设备唯一ID
    pjysdk.set_card(card)  # 设置卡密
    
    ret = pjysdk.card_login()  # 卡密登录
    if ret.code != 0:  # 登录失败
        print(ret.message)
    return True