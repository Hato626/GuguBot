from sys import path
from typing import Set
#from graia.application.message.elements.internal import FlashImage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.element import At
from graia.ariadne.message.element import Image
from graia.ariadne.app import Ariadne

from graia.ariadne.model import Group, Member, MiraiSession

from graia.ariadne.message import *
from graia.ariadne.event import *

from graia.saya import Saya, Channel
from pydantic.utils import KeyType
from PIL import Image as Imagea
from urllib.parse import quote
from pathlib import Path
import urllib.request
import numpy as np
import datetime
import asyncio
import aiohttp
import sqlite3
import random
import time
import json
import ssl
import os

from regex import R

 
ssl._create_default_https_context = ssl._create_unverified_context


# 插件信息
__name__ = "Setu"
__description__ = "发送色图"
__author__ = "帝王圣鸽"
__usage__ = "咕咕+来<数量>张<关键字/高清>色图"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)



@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    sender: Member

):
    if "咕咕" in message.asDisplay() or '@2484162372' in message.asDisplay():
        msg = message.asDisplay()
        request = ["来",
                "來",
                "发",
                "發",
                "给",
                "給",
                "开"]
        unit = ["张",
                "張",
                "个",
                "幅",
                "個",
                "點",
                "点",
                "份"]
        se = ["色",
            "涩",
            "塞",
            "瑟",
            "好",
            "坏"]
        tu = ["图",
            "涂",
            "圖"]

        proxy = "i.pximg.pixiv.chinjufu.club"

        if containsAny(msg, request) and containsAny(msg, unit) and containsAny(msg, se) and containsAny(msg, tu):
            ##获取各关键字出现位置
            for i in range(0,len(request)):
                if request[i] in msg:
                    requestpoint = request[i]
                    requestPos=msg.find(requestpoint)
                    requestPos1 = requestPos + 1
                    break
            for i in range(0,len(unit)):
                if unit[i] in msg:
                    unitpoint = unit[i]
                    unitPos = msg.find(unitpoint)
                    break
            for i in range(0,len(se)):
                if se[i] in msg:
                    sepoint = se[i]
                    sePos = msg.find(sepoint)
                    break
            for i in range(0,len(tu)):
                if tu[i] in msg:
                    tupoint = tu[i]
                    tuPos = msg.find(tupoint)
                    break
            if requestPos < unitPos < sePos < tuPos:
                ##获取色图数量
                if msg[requestPos1:unitPos].isdigit():
                    if requestPos1 == unitPos:
                        num = 1
                    else:
                        num = int(msg[requestPos1:unitPos])
                else:
                    if msg[requestPos1:unitPos] == '':
                        num = 1
                    else:
                        num = chinese2digits(msg[requestPos1:unitPos])
                if num > 20:num = 20
                
                oneSetuPrise = 1
                reducemoney = num * oneSetuPrise
                
                ##获取Keyword及R18状态
                if unitPos + 1 == sePos:
                    Keyword = -1
                else:
                    Keyword = msg[unitPos + 1:sePos]
                Keyword = str(Keyword)
                KeywordStr = Keyword
                if '的' in Keyword:
                    Keyword = Keyword.replace("的","")
                if 'r18' in Keyword:
                    Keyword = Keyword.replace("r18","")
                    Keyword = Keyword.replace("R18","")
                    R18_state = True
                else:
                    R18_state = False


                ##判断是否有高清
                if '高清' in Keyword:
                    Keyword = Keyword.replace("高清","")
                    Usetype = 'original'
                else:
                    Usetype = 'regular'
                ##将Keyword转换为二进制
                Keyword = quote(Keyword)
                ##获取色图，并缓存
                

                ##尝试使用tag获取api
                GetUrlTime = time.time()
                if R18_state == True:
                    response = urllib.request.urlopen("https://api.lolicon.app/setu/v2?r18=1&proxy=" + proxy + "&num=" + str(num) + "&size=" + Usetype + "&tag=" + Keyword)
                else:
                    response = urllib.request.urlopen("https://api.lolicon.app/setu/v2?r18=0&proxy=" + proxy + "&num=" + str(num) + "&size=" + Usetype + "&tag=" + Keyword)
                info = json.loads(response.read().decode("utf-8"))
                ##若tag无法获取使用keyword获取
                if info['data'] == []:
                    print('尝试使用keyword获取')
                    if R18_state == True:
                        response = urllib.request.urlopen("https://api.lolicon.app/setu/v2?r18=1&proxy=" + proxy + "&num=" + str(num) + "&size=" + Usetype + "&keyword=" + Keyword)
                    else:
                        response = urllib.request.urlopen("https://api.lolicon.app/setu/v2?r18=0&proxy=" + proxy + "&num=" + str(num) + "&size=" + Usetype + "&keyword=" + Keyword)
                    info = json.loads(response.read().decode("utf-8"))
                print('从源站获取色图链接用时: ' + str(time.time() - GetUrlTime))
                
                
                #临时构建info##如果是KK
                if KeywordStr == "Kekon" or KeywordStr == "kekon" or KeywordStr == "血痕" or KeywordStr == "kk":
                    info = {}
                    info["data"] = [{'urls':{Usetype:'https://api.nmsl.fun/Kekon.jpg'}}]
                
                if info['data'] != []:
                    Tasks = []
                    PathLib = []
                    ##缓存
                    for i in range(0,len(info['data'])):
                        ##传入色图地址，群组id,色图质量,异步执行
                        Task = asyncio.create_task(GetSetu(group.id, info['data'][i]['urls'][Usetype], Usetype))
                        Tasks.append(Task)
                        ##构建本地文件中文件列表
                        RealPath = os.getcwd() + '/modules/Setu/setucache/' + str(info['data'][i]['urls'][Usetype].split('/')[-1])
                        PathLib.append(RealPath)
                    DownloadTime = time.time()
                    await asyncio.wait(Tasks)
                    print('下载用时: ' + str(time.time() - DownloadTime))
                else:
                    PathLib = []

                
                ##是否禁言
                Muterange = 0
                randomNum = random.randint(0,100)
                if randomNum < Muterange:Mutestate = True
                else: Mutestate = False

                ##读取色图一小时内发送次数
                qqId = 956162597
                qqId = sender.id
                MaxSetuNum = 60
                SetuNum, Oldhour = GetSqlite3(qqId)
                if SetuNum <= MaxSetuNum:
                    OutOfMaxNum = False
                else:
                    OutOfMaxNum = True
                

                if Mutestate == False and OutOfMaxNum == False:
                    ##发送
                    Money = GetMoney(sender.id)
                    if Money >= num:
                        if 'r18' in KeywordStr:
                            await app.sendGroupMessage(group, MessageChain.create([Plain(text="?")]))
                        else:
                            if info['data'] == []:
                                await app.sendGroupMessage(group, MessageChain.create([Plain(text="呜呜，咕咕找不到你要的色图")]))
                            else:
                                if str(Keyword) != '-1':
                                    await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="\n咕咕找到咯,这是" + KeywordStr + "涩图")]))
                                    for i in range(0,len(PathLib)):
                                        await app.sendGroupMessage(group, MessageChain.create([Image(path=PathLib[i])]))
                                else:
                                    await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="\n咕咕找到咯")]))
                                    for i in range(0,len(PathLib)):
                                        await app.sendGroupMessage(group, MessageChain.create([Image(path=PathLib[i])]))
                                await app.sendGroupMessage(group, MessageChain.create([
                                    Plain(text='扣除痕币 ' + str(reducemoney) +  ' 枚\n'),
                                    Plain(text="剩余痕币: "),
                                    Plain(text=Money - reducemoney ),
                                    Plain(text=" 枚")
                                    ]))
                        print("此时发送成功")            
                        WriteSqlite3(qqId)
                        SetMoney(sender.id,'reduce',reducemoney)
                    else:
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text="爬，你的痕币不够！")]))
                else:
                    try:
                        #禁言
                        rangenum = random.randint(1,1200)
                        d,h,m,s =changetime(rangenum)
                        RealTime =  m + '分' + s + '秒'
                        await app.mute(group.id, sender.id, rangenum)
                        MessageChainA = MessageChain.create([At(sender.id),Plain("\n已中奖\n----------------\n"),Plain(RealTime)])
                        await app.sendGroupMessage(group, MessageChainA)
                    except:
                        await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="\n注意节制~")]))
            


def containsAny(seq, aset):
    return True if any(i in seq for i in aset) else False

def AddNoise(ImgPath):
    img = np.array(Imagea.open(ImgPath))
    rows,cols,dims=img.shape
    rangenum = random.randint(10,40)
    for i in range(rangenum):
        x=np.random.randint(0,rows)
        y=np.random.randint(0,cols)
        img[x,y,:]=random.randint(0,255)

    im = Imagea.fromarray(img)
    im.save(ImgPath)




async def GetSetu(groupid, SetuUrl, Usetype):
    async with aiohttp.ClientSession(headers=[('User-agent', 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]) as session:
        async with session.get(SetuUrl) as r:
            pic = await r.read()
            await SaveSetu(pic, SetuUrl.split('/')[-1])
            return os.getcwd() + '/modules/Setu/setucache/' + SetuUrl.split('/')[-1]

async def SaveSetu(pic, path):
    Path(os.getcwd() + '/modules/Setu/setucache/' + path).write_bytes(pic)
    AddNoise(os.getcwd() + '/modules/Setu/setucache/' + path)




# async def getsetu(groupid,info,Usetype):
#     if groupid == 984392483:
#         if info['data'] != []:
#             PathLib = []
#             for i in range(0,len(info['data'])):
#                 setuid = random.randint(0,99999)
#                 realpath = os.getcwd() + '/modules/Setu/setucache/buse/' + str(setuid) + '.jpg'
#                 ##获取色图
#                 setuurl = 'https://acg.yanwz.cn/wallpaper/api.php'
#                 print(setuurl)
#                 opener = urllib.request.build_opener()
#                 opener.addheaders = [('User-agent', 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
#                 urllib.request.install_opener(opener)
#                 urllib.request.urlretrieve(setuurl, realpath)   #realpath为本地保存路径
#                 PathLib.append(realpath)
#                 ##随机修改1像素
#                 AddNoise(realpath)
#                 #调用wget
#                 #os.popen("wget -P " + realpath + " " + setuurl)
#                 ##图片压缩
#                 #print(realpath)
#                 #minpath, minsize = compress_image(realpath, realpath)
#                 #print(minpath, minsize)
#         else:
#             PathLib = []
#             PathLib.append("/mnt/file/SetuSql/Kekon.jpg")
#         print("此时从源站获取图片成功")
#     else:
#         # ##缓存
#         if info['data'] != []:
#             PathLib = []
#             for i in range(0,len(info['data'])):
#                 realpath = os.getcwd() + '/modules/Setu/setucache/' + info['data'][i]['urls'][Usetype].split('/')[-1]
#                 ##获取色图
#                 setuurl = info['data'][i]['urls'][Usetype]
#                 print(setuurl)
#                 opener = urllib.request.build_opener()
#                 opener.addheaders = [('User-agent', 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
#                 urllib.request.install_opener(opener)
#                 urllib.request.urlretrieve(setuurl, realpath)   #realpath为本地保存路径
#                 PathLib.append(realpath)
#                 ##随机修改1像素
#                 AddNoise(realpath)
#                 #调用wget
#                 #os.popen("wget -P " + realpath + " " + setuurl)
#                 ##图片压缩
#                 #print(realpath)
#                 #minpath, minsize = compress_image(realpath, realpath)
#                 #print(minpath, minsize)
#         else:
#             PathLib = []
#             PathLib.append("/mnt/file/SetuSql/Kekon.jpg")
#         print("此时从源站获取图片成功")
#     return PathLib

# 把汉字变为阿拉伯数字
def chinese2digits(chinese_str):
    t = chinese_str
    if t is None or t.strip() == "":
        raise Exception("input error for %s" % chinese_str)
    t = t.strip()
    t = t.replace("百十", "百一十")
    common_used_numerals = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                            '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
    total = 0
    r = 1
    for i in range(len(t) - 1, -1, -1):
        val = common_used_numerals.get(t[i])
        if val is None:
            return 1
        if val >= 10 and i == 0:
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total


##时间转换
def changetime(y):
    h=int(y//3600 % 24)
    d = int(y // 86400)
    m =int((y % 3600) // 60)
    s = round(y % 60,2)
    h=convert_time_to_str(h)
    m=convert_time_to_str(m)
    s=convert_time_to_str(s)
    d=convert_time_to_str(d)
    return d,h,m,s


def convert_time_to_str(time):
    #时间数字转化成字符串，不够10的前面补个0
    if (time < 10):
        time = '0' + str(time)
    else:
        time=str(time)
    return time


def WriteSqlite3(qqId):
    num, Oldhour = GetSqlite3(qqId)
    num = num + 1
    connect = sqlite3.connect(os.getcwd() + '/modules/Setu/Setuhour.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS setunum(qqId text NOT NULL UNIQUE, num text, hour text)") ##创建表
    cursor.execute("insert or replace into setunum values (?,?,?)", (str(qqId), str(num), str(Oldhour)))
    connect.commit()
    connect.close()

def GetSqlite3(qqId):
    hour = datetime.datetime.now().hour
    connect = sqlite3.connect(os.getcwd() + '/modules/Setu/Setuhour.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS setunum(qqId text NOT NULL UNIQUE, num text, hour text)") ##创建表
    cursor.execute("SELECT * FROM setunum WHERE qqId = " + "'" + str(qqId) + "' and hour = '" + str(hour) + "'")
    for row in cursor:
        num = row[1]
        Oldhour = row[2]
    try:
        if str(hour) != Oldhour:
            try:
                cursor.execute("insert or replace into setunum values (?,?,?)", (str(qqId), str(0), str(hour)))
                connect.commit()
            except:
                pass
        connect.close()
        return int(num), int(Oldhour)
    except:
        connect.close()
        return 1, hour


def GetMoney(qqId):
    connect = sqlite3.connect(os.getcwd() + '/modules/Money.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Money(qqId text NOT NULL UNIQUE, money text)") ##创建表
    cursor.execute("SELECT * FROM Money WHERE qqId = " + "'" + str(qqId) + "'")
    ##返回获取值
    for row in cursor:
        Money = row[1]
    try:
        connect.close()
        return int(Money)
    except UnboundLocalError:
        connect.close()
        return 0

def SetMoney(qqId, Type, quantity):
    OldMoney = GetMoney(qqId)
    if OldMoney == None: OldMoney = 0
    if Type == 'add':
        NewMoney = OldMoney + int(quantity)
    elif Type == 'reduce':
        NewMoney = OldMoney - int(quantity)
    elif Type == 'set':
        NewMoney = int(quantity)
    connect = sqlite3.connect(os.getcwd() + '/modules/Money.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Money(qqId text NOT NULL UNIQUE, money text)") ##创建表
    cursor.execute("insert or replace into Money values (?,?)", (str(qqId), str(NewMoney)))
    connect.commit()
    connect.close()