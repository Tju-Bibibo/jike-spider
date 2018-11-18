#coding == utf-8
import requests
from bs4 import BeautifulSoup
import pymysql
import os
import re
import json
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import traceback
import sys
sys.setrecursionlimit(1000000)

def html_downloader(url,payload,access_token):
    headers = {"Accept":"application/json",
    "App-Version":"4.1.0",
    "Content-Type":"application/json",
    "Origin":"https://web.okjike.com",
    "platform":"web",
    "Referer":"https://web.okjike.com/user/JTYSMHXD/follower",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    headers["x-jike-access-token"] = str(access_token)
    r = requests.post(url,headers= headers, data=json.dumps(payload))
    content = r.text
    return content
def get_payload(content,usern):
    text = json.loads(content)
    loadkey = text["loadMoreKey"]
    payload ={}
    payload["loadMoreKey"] = loadkey #从上一个getfollowedlist里面得到的
    payload["username"] = usern #这里就是要爬取的人的username
    payload["limit"] = 20
    return payload
def parser(content):
    text = json.loads(content)
    data = text["data"]
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='jike', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    for i in data:
        #用户个人信息
        username = i["username"] #个人id
        screenName = i["screenName"]#昵称
        createdAt = i["createdAt"]#注册日
        updatedAt = i["updatedAt"]#最后一次登陆
        isVerified = i["isVerified"]#是否即刻认证用户
        verifyMessage = i["verifyMessage"] #
        briefIntro = i["briefIntro"] #个人简介&什么话题贡献者
        bio = None#i["bio"] #个人简介
        thumbnailUrl = i["avatarImage"]["thumbnailUrl"]#头像缩略图
        picUrl = i["avatarImage"]["picUrl"] #头像图片

        #这里是处理有些人的个人简介里面会出现表情字符导致导入utf-8编码的数据库错误
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        briefIntro = highpoints.sub(u'??', briefIntro)
        briefIntro =briefIntro.replace("\'"," ")
        briefIntro = str(briefIntro)
        #由于有些人的性别，城市，国家信息没有填写，也即是获得的json包里面没有这些信息，故导入数据库中按照空值处理
        try:
            gender=i["gender"]
            city= i["city"]
            country =i["country"]
            province =i["province"]
        except:
            gender=None
            city= None
            country =None
            province =None
        following = i["following"]
        ref = i["ref"]
        #用户状态

        topicSubscribed= i["statsCount"]["topicSubscribed"] #话题参与
        topicCreated =i["statsCount"]["topicCreated"]     #话题创建
        followedCount=i["statsCount"]["followedCount"]    #被关注的人数
        followingCount=i["statsCount"]["followingCount"]  #关注的人数
        highlightedPersonalUpdates=i["statsCount"]["highlightedPersonalUpdates"]
        liked=i["statsCount"]["liked"]        #被赞数
        #print(username, screenName,briefIntro)

        sql1 = "select count(id) from jike_user where username = ('%s')" %(username) #判断数据是否已出现在数据中
        cursor.execute(sql1)
        numb = cursor.fetchone()
        if numb[0] == 0:
            sql = "INSERT INTO jike_user(username,screenName,createdAt,updatedAt,isVerified,verifyMessage,briefIntro, \
                                         bio,thumbnailUrl,picUrl,gender,city,country,province,following, \
                                         ref,topicSubscribed,topicCreated,followedCount,followingCount,\
                                         highlightedPersonalUpdates,liked) \
                    values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                    %(username,screenName,createdAt,updatedAt,isVerified,verifyMessage,briefIntro, \
                                         bio,thumbnailUrl,picUrl,gender,city,country,province,following, \
                                         ref,topicSubscribed,topicCreated,followedCount,followingCount,\
                                         highlightedPersonalUpdates,liked)
            try:
                cursor.execute(sql)
            except:
                pass
        else:
            pass

    db.commit()
    # 关闭数据库连接
    db.close()
global idd
def spider(url,payload,usern,access_token):
    content = html_downloader(url,payload,access_token)
    payload = get_payload(content,usern)
    parser(content)
    print(payload)
    if payload["loadMoreKey"] == None:
        return 0
    spider(url,payload,usern,access_token)
def auto_spider(idd,access_token):
    url = "https://app.jike.ruguoapp.com/1.0/userRelation/getFollowerList"
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='jike', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "SELECT username,id FROM jike_user where id >('%s')" \
          " and followedCount <10000" %(idd)
    cursor.execute(sql)
    list_all = cursor.fetchall()
    payload = {}
    for i in list_all:
        usern = i[0]
        payload['loadMoreKey'] = None
        payload['username'] = usern
        payload['limit'] = 20
        try:
            spider(url,payload,usern,access_token)
        except:
            return i[1]
        print(i[0],i[1],"\n")
global access_token
global x_refresh_token
def refresh_token(refresh_token):
    url = "https://app.jike.ruguoapp.com/app_auth_tokens.refresh"
    headers = {"Origin":"https://web.okjike.com",
               "Referer":"https://web.okjike.com/user/JTYSMHXD/follower",
               "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    headers["x-jike-refresh-token"] = str(refresh_token)
    r = requests.get(url,headers= headers)
    print(r.status_code)
    content = r.text
    return content
def final_spider(idd,x_refresh_token):
    token = refresh_token(x_refresh_token)
    token = json.loads(token)
    x_refresh_token = token["x-jike-refresh-token"]
    access_token = token["x-jike-access-token"]
    idd = auto_spider(idd,access_token)
    return final_spider(idd,x_refresh_token)
if __name__ == "__main__":
    x_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiejlqMHg2Z1JSR05iM1lZQ2daUHdOM0M2K3F4UkVlbmJvSkVabU92RXdJdzN1UEV5WDY4RStERGFjTXFMd2ZFdGI5U2ZGMjd3ZVJITlVEeHlnTFk1OHRneWxMTEJjMnBRbjFBT3FiMXNGUXh6dVYyZmYwUzVUMnpmTmR2WFRoRDdQVEhJYlQxTllkS3dSM2E5MHl3OEk5RWdEVlJiYllcL2JPTnZ4azRLeDNpYz0iLCJ2IjozLCJpdiI6Imk1Y0pMUHFma2NYOHZXWElrWjJBbkE9PSIsImlhdCI6MTU0MjI1ODgxMy43MjV9.3hBQxU2M86t1zP0PXeZc2WWspZu70XOz_FJ5nLGEKVo"
    final_spider(77000,x_refresh_token)

#自动爬取有两个限制：一是如何遍历所有人，2是cookie如何保持
