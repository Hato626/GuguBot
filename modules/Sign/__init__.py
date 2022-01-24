from pydantic.utils import KeyType
from graia.saya import Saya, Channel
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
import os
import sqlite3
import json
import datetime
import time
import random


# 插件信息
__name__ = "签到"
__description__ = "签到"
__author__ = "帝王圣鸽"
__usage__ = "发送消息即可触发"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    if message.asDisplay() == '签到' or message.asDisplay() == '打卡' or message.asDisplay() == 'sign':
        info = GetSql(sender.id, 'id')
        # 数据结构
        # {
        #     GroupId:{
        #         Year:{
        #             Month:{
        #                 SignList:[]
        #                 SignTime:{
        #                     Day: Time
        #                 }
        #             }
        #         }
        #     }
        # }
        ##判断是否为第一次签到，若是则构造数据
        if info == None:
            info = {}
            info[str(group.id)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignList"] = []
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignTime"] = {}
        ##判断本群是否第一次签到,若无则构造数据
        if str(group.id) not in info:
            info[str(group.id)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignList"] = []
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignTime"] = {}
        ##判断本年是否签到,若无则构造今年数据
        if str(datetime.datetime.now().year) not in info[str(group.id)]:
            print("今年无签到")
            info[str(group.id)][str(datetime.datetime.now().year)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignList"] = []
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignTime"] = {}
        ##判断本月是否签到,若无则构造本月数据
        if str(datetime.datetime.now().month) not in info[str(group.id)][str(datetime.datetime.now().year)]:
            print("本月无签到")
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)] = {}
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignList"] = []
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignTime"] = {}
        
        ##判断今日是否签到
        ThisMonthSignInfo = info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignList']
        if datetime.datetime.now().day in ThisMonthSignInfo: SignState = True
        else:SignState = False

        ##发送反馈
        if SignState == True:
            await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="今天已经签到过了，不能重复签到哦")]))
        else:
            ##签到成功时更新数据库
            ThisMonthSignInfo.append(datetime.datetime.now().day)
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignList'] = ThisMonthSignInfo
            info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignTime'][datetime.datetime.now().day] = time.time()
            WriteSql(sender.id, info)
            ##计算本日签到名次
            SignRanking = GetSignTop(group.id)
            SignRanking = len(SignRanking)
            SignRankingStr = '今日你是第 ' + str(SignRanking) + ' 个签到哦\n'
            ##计算本月签到天数
            ThisMonthCheckInDays = len(ThisMonthSignInfo)
            ##随机今日获取金币数
            RandomMoney = random.randint(5,12)
            ##更新金币数据库
            SetMoney(sender.id, 'add', RandomMoney)
            ##获取总金币数
            Money = GetMoney(sender.id)
            await app.sendGroupMessage(group, MessageChain.create([
                At(sender.id),
                Plain(text="签到成功\n"),
                Plain(text=SignRankingStr),
                Plain(text="本月签到天数: "),
                Plain(text=ThisMonthCheckInDays),
                Plain(text="天\n"),
                Plain(text="本次获取痕币数: "),
                Plain(text=RandomMoney),
                Plain(text=" 枚\n"),
                Plain(text="总痕币数: "),
                Plain(text=Money),
                Plain(text=" 枚")
            ]))
    if message.asDisplay() == '签到明细' or message.asDisplay() == '打卡明细':
        Info = GetSql(sender.id, 'id')
        SignList = Info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignList']
        SignTime = Info[str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignTime']
        NewSignTime = {}
        for day in SignTime:
            Time = time.strftime("%H:%M:%S", time.localtime(SignTime[day]))
            NewSignTime[day] = Time
        SignDayStr = ''
        for i in NewSignTime:
            SignDayStr = SignDayStr + i + '日: ' + NewSignTime[i] + '\n'
        SignDayStr = SignDayStr[:-1]
        await app.sendGroupMessage(group, MessageChain.create([
                At(sender.id),
                Plain(text="\n"),
                Plain(text="本月签到天数: "),
                Plain(text=len(SignList)),
                Plain(text="天\n"),
                Plain(text=SignDayStr)
            ]))

    if message.asDisplay() == '签到排行榜' or message.asDisplay() == '打卡排行榜' or  message.asDisplay() == '签到排行' or  message.asDisplay() == '签到排名':
        Info = GetSql(sender.id, 'all')
        ##获取每人今月签到天数List
        SignDayQuantity = {}
        for i in Info:
            if str(group.id) in Info[i]:
                if str(datetime.datetime.now().year) in Info[i][str(group.id)]:
                    if str(datetime.datetime.now().month) in Info[i][str(group.id)][str(datetime.datetime.now().year)]:
                        SignDayQuantity[i] = len(Info[i][str(group.id)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignList'])
        SignDayQuantity = dict(sorted(SignDayQuantity.items(), key = lambda kv:kv[1], reverse=True))
        SignDayQuantityStr = ''
        Num = 0
        for i in SignDayQuantity:
            if Num < 10:
                member = await app.getMember(group,int(i))
                name = member.name
                SignDayQuantityStr = SignDayQuantityStr + name + '(' + str(i) + ')' + ' : ' + str(SignDayQuantity[i]) + ' 天' + '\n'
                Num = Num + 1
            else:
                pass
        SignDayQuantityStr = SignDayQuantityStr[:-1]
        await app.sendGroupMessage(group, MessageChain.create([
                Plain(text=SignDayQuantityStr)
            ]))
    


def WriteSql(qqId, info):
    connect = sqlite3.connect(os.getcwd() + '/modules/Sign/Sign.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Sign(qqId text NOT NULL UNIQUE, Signinfo text)") ##创建表
    cursor.execute("insert or replace into Sign values (?,?)", (str(qqId), str(json.dumps(info))))
    connect.commit()
    connect.close()

def GetSql(qqId, Type):
    connect = sqlite3.connect(os.getcwd() + '/modules/Sign/Sign.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Sign(qqId text NOT NULL UNIQUE, Signinfo text)") ##创建表
    if Type == 'id':
        cursor.execute("SELECT * FROM Sign WHERE qqId = " + "'" + str(qqId) + "'")
        ##返回获取值
        for row in cursor:
            info = row[1]
        try:
            connect.close()
            return json.loads(info)
        except UnboundLocalError:
            connect.close()
            return None
    else:
        cursor.execute("SELECT * FROM Sign")
        info = {}
        ##返回获取值
        for row in cursor:
            info[row[0]] = json.loads(row[1])
        try:
            connect.close()
            return info
        except UnboundLocalError:
            connect.close()
            return None
    


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
        return None

def SetMoney(qqId, Type, quantity):
    OldMoney = GetMoney(qqId)
    if OldMoney == None: OldMoney = 0
    if Type == 'add':
        NewMoney = OldMoney + quantity
    elif Type == 'reduce':
        NewMoney = OldMoney - quantity
    connect = sqlite3.connect(os.getcwd() + '/modules/Money.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Money(qqId text NOT NULL UNIQUE, money text)") ##创建表
    cursor.execute("insert or replace into Money values (?,?)", (str(qqId), str(NewMoney)))
    connect.commit()
    connect.close()


def GetSignTop(groupid):
    Info = GetSql('all', 'all')
    ##获取每人今月签到天数List
    SignTime = {}
    for i in Info:
        if str(groupid) in Info[i]:
            if str(datetime.datetime.now().year) in Info[i][str(groupid)]:
                if str(datetime.datetime.now().month) in Info[i][str(groupid)][str(datetime.datetime.now().year)]:
                    if datetime.datetime.now().day in Info[i][str(groupid)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignList']:
                        SignTime[i] = Info[i][str(groupid)][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]['SignTime'][str(datetime.datetime.now().day)]
    SignTime = dict(sorted(SignTime.items(), key = lambda kv:kv[1], reverse=True))
    return SignTime
    