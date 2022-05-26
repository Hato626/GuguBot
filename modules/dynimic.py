from nturl2path import url2pathname
from webbrowser import get
from bilibili_api import dynamic,app,user
import asyncio
import json
import sqlite3
import os
import re
import requests

from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage, FriendMessage, Friend
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At
from graia.scheduler.saya import SchedulerSchema, GraiaSchedulerBehaviour
from graia.scheduler import timers 

# 插件信息
__name__ = "动态监控"
__description__ = "动态监控"
__author__ = "帝王圣鸽"
__usage__ = "自动监控,无需操作"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法:{__usage__}")
channel.author(__author__)


uid = 9561918
#uid = 110140580
groupid = [371815444, 956162597]
DynamicPushRule = {
    'AtAll':False,
    'Text': 'Kekon发送新动态啦！\n%Url% \n动态类型:%type% \n内容:%content% \n时间:%time%'
    }
User = user.User(uid)




@channel.use(SchedulerSchema(timers.every_custom_seconds(10)))
async def something_scheduled(app: Ariadne):
    await main(app)

async def main(app):
    hasmore = 1
    offset  = 0
    while hasmore == 1:
        dynamics = await getDynamic(User,offset)
        hasmore = dynamics['has_more']
        offset = dynamics['next_offset']
        ##print(hasmore,dynamics['next_offset'])
        if hasmore == 1:
            for i in dynamics['cards']:
                ##Ture为数据库中有记录
                if await Comparative(i):
                    pass
                else:
                    await SetHistory(i)
                    await SendGroupMessage_NewDynamic(groupid, i, app)
        



    


async def getDynamic(User,offset):
    dynamics = await user.User.get_dynamics(User,offset)
    return dynamics



async def Comparative(NewInfo):
    State = await getHistory(NewInfo['desc']['dynamic_id'], 'state')
    return State
    



async def getHistory(dynamic_id, type):
    connect = sqlite3.connect(os.getcwd() + '/modules/DynamicHistory.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS History(dynamic_id text NOT NULL UNIQUE, dynamic_info text)") ##创建表
    if type == 'state':
        cursor.execute("SELECT * FROM History WHERE dynamic_id = " + "'" + str(dynamic_id) + "'")
        ##返回获取值
        result = cursor.fetchall()
        if result != []:
            connect.close()
            return True
        else:
            connect.close()
            return False

async def SetHistory(dynamics):
    connect = sqlite3.connect(os.getcwd() + '/modules/DynamicHistory.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS History(dynamic_id text NOT NULL UNIQUE, dynamic_info text)") ##创建表
    cursor.execute("insert or replace into History values (?,?)", (str(dynamics['desc']['dynamic_id']), str(dynamics)))
    connect.commit()
    connect.close()

async def SendGroupMessage_NewDynamic(groupid, dynamic, app):
    message = await ReMsg(DynamicPushRule['Text'], dynamic)
    await PushMessage(message, groupid, app)


async def ReMsg(msg,dynamic):
    dynamicid = dynamic['desc']['dynamic_id']
    type = dynamic['desc']['type']
    timestamp = dynamic['desc']['timestamp']
    Url = 'https://t.bilibili.com/' + str(dynamicid)
    #内容
    if type == 1:
        ##转发动态
        typeStr = '转发动态'
        content = dynamic['card']['item']['content']
    elif type == 8:
        ##投稿视频
        typeStr = '投稿视频'
        content = dynamic['card']['desc']
    elif type == 64:
        ##文章
        typeStr = '文章'
        content = dynamic['card']['title']
        ##文章id dynamic['card']['id']
    elif type == 2:
        ##普通动态(可能加图片)
        # "pictures": [
        #     {
        #         "img_height": 681,
        #         "img_size": 415.2958984375,
        #         "img_src": "https://i0.hdslb.com/bfs/album/4bfc21ebb0adbb0debf45cee1772b42db5ec01df.png",
        #         "img_tags": null,
        #         "img_width": 721
        #     }
        # ]
        typeStr = '混合动态'
        content = dynamic['card']['item']['description']
        #pictureUrl = dynamic['card']['item']['pictures']['img_src']
    elif type == 4:
        typeStr = '图片动态'
        content = '好多好多图片:)'

    Newmessage = msg
    Newmessage = re.sub('%Url%',Url,Newmessage)
    Newmessage = re.sub('%type%',typeStr,Newmessage)
    Newmessage = re.sub('%content%',content,Newmessage)
    Newmessage = re.sub('%time%',str(timestamp),Newmessage)

    return Newmessage


async def PushMessage(msg, groupid, app):
    messagechain = MessageChain.create([
        Plain(text=msg)
        ])
    for i in groupid:
        await app.sendGroupMessage(i, messagechain)