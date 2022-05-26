from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage, FriendMessage, Friend
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At
import os
import sqlite3
import datetime
import re
import json


# 插件信息
__name__ = "聊天指令"
__description__ = "聊天指令"
__author__ = "帝王圣鸽"
__usage__ = "发送消息即可触发"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

UseMoney = True
OnePointUseMoney = 4
ecoType = '痕币'

Administrator = ["1321008977"]

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    if containsAny(str(sender.id),Administrator):
        ##增加痕币
        AddMoneyRule = "[咕咕][增加]<User>[的]<Num>[枚痕币]"
        if IsHaveQuantitative(message.asDisplay(),AddMoneyRule):
            Variable = FindVariable(message.asDisplay(),AddMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'add', Quantity)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))
        ##设置痕币
        SetMoneyRule = "[咕咕][设置]<User>[的][痕币][为]<Num>[枚]"
        if IsHaveQuantitative(message.asDisplay(),SetMoneyRule):
            Variable = FindVariable(message.asDisplay(),SetMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'set', Quantity)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))
        ##减少痕币
        ReduceMoneyRule = "[咕咕][减少]<User>[的]<Num>[枚痕币]"
        if IsHaveQuantitative(message.asDisplay(),ReduceMoneyRule):
            Variable = FindVariable(message.asDisplay(),ReduceMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'reduce', Quantity)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))

        ##清除你画我猜进程
        ClearTPIGRule = "[咕咕][结束]<User>[的][你画我猜进程]"
        if IsHaveQuantitative(message.asDisplay(),ClearTPIGRule):
            Variable = FindVariable(message.asDisplay(),ClearTPIGRule)
            UserId = Variable[0]
            WriteYPIGSqlite3(UserId, 'EndGame', None)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text="操作成功\n"),
                Plain(text="状态码: "),
                Plain(text=GetYPIGSqlite3(UserId, 'state'))
            ]))

        ##清除今日打卡成绩
        ClearSignRule = "[咕咕][清除]<User>[在]<GroupId>[的][今日签到记录]"
        if IsHaveQuantitative(message.asDisplay(),ClearSignRule):
            Variable = FindVariable(message.asDisplay(),ClearSignRule)
            UserId = Variable[0]
            GroupId = Variable[1]
            Info = GetSignSql(UserId,'id')
            Info[GroupId][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignList"].remove(datetime.datetime.now().day)
            Info[GroupId][str(datetime.datetime.now().year)][str(datetime.datetime.now().month)]["SignTime"].pop(str(datetime.datetime.now().day))
            WriteSignSql(UserId, Info)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text="操作成功")
            ]))


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Friend,
): 
    if containsAny(str(sender.id),Administrator):
        ##增加痕币
        AddMoneyRule = "[咕咕][增加]<User>[的]<Num>[枚痕币]"
        if IsHaveQuantitative(message.asDisplay(),AddMoneyRule):
            Variable = FindVariable(message.asDisplay(),AddMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'add', Quantity)
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))
        ##设置痕币
        SetMoneyRule = "[咕咕][设置]<User>[的][痕币][为]<Num>[枚]"
        if IsHaveQuantitative(message.asDisplay(),SetMoneyRule):
            Variable = FindVariable(message.asDisplay(),SetMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'set', Quantity)
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))
        ##减少痕币
        ReduceMoneyRule = "[咕咕][减少]<User>[的]<Num>[枚痕币]"
        if IsHaveQuantitative(message.asDisplay(),ReduceMoneyRule):
            Variable = FindVariable(message.asDisplay(),ReduceMoneyRule)
            UserId = Variable[0]
            Quantity = Variable[1]
            SetMoney(UserId, 'reduce', Quantity)
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(text="设置成功\n"),
                Plain(text="余额: "),
                Plain(text=GetMoney(UserId)),
                Plain(text=" "),
                Plain(text=ecoType)
            ]))

        ##清除你画我猜进程
        ClearTPIGRule = "[咕咕][结束]<User>[的][你画我猜进程]"
        if IsHaveQuantitative(message.asDisplay(),ClearTPIGRule):
            Variable = FindVariable(message.asDisplay(),ClearTPIGRule)
            UserId = Variable[0]
            WriteYPIGSqlite3(UserId, 'EndGame', None)
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(text="操作成功")
            ]))


    
    
def FindVariable(msg,Rule):
    RuleListA = re.split('\[.*?\]', Rule) ##<>列表
    RuleListB = re.findall('\[.*?\]', Rule) ##[]列表

    ReturnList = []
    for i in range(len(RuleListA)):
        if RuleListA[i] != '':
            RuleB1 = RuleListB[i - 1]
            RuleB2 = RuleListB[i]
            ##获取真正的关键字
            RuleB1 = RuleB1[1:-1]
            RuleB2 = RuleB2[1:-1]
            Variable = re.findall(RuleB1 + '(.*?)' + RuleB2, msg) ##<>列表
            ReturnList.append(Variable[0])
    return ReturnList


def IsHaveQuantitative(msg,Rule):
    State = True
    RuleListB = re.findall('\[(.*?)\]', Rule) ##[]列表
    QuantitativePos = []
    for i in RuleListB:
        QuantitativePos.append(msg.find(i))
    if -1 not in QuantitativePos:
        TemQuantitativePos = []
        for i in range(len(QuantitativePos)):
            TemQuantitativePos.append(QuantitativePos[i])
            if i != 0:
                if QuantitativePos[i] < TemQuantitativePos[i - 1]:
                    State = False
                    break
    else:
        State = False
    return State
    



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


def WriteYPIGSqlite3(qqId, Type, info):
    if Type == 'CreatNewGame':
        connect = sqlite3.connect(os.getcwd() + '/modules/YouDrawIGuess/GameInfo.db')
        cursor = connect.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS GameInfo(qqId text NOT NULL UNIQUE, state text, question text, qqgroup text)") ##创建表
        cursor.execute("insert or replace into GameInfo values (?,?,?,?)", (str(qqId), str(1), None, str(info)))
        connect.commit()
        connect.close()
    if Type == 'question':
        group = GetYPIGSqlite3(qqId, 'group')
        connect = sqlite3.connect(os.getcwd() + '/modules/YouDrawIGuess/GameInfo.db')
        cursor = connect.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS GameInfo(qqId text NOT NULL UNIQUE, state text, question text, qqgroup text)") ##创建表
        cursor.execute("insert or replace into GameInfo values (?,?,?,?)", (str(qqId), str(2), str(info), str(group)))
        connect.commit()
        connect.close()
    if Type == 'EndGame':
        connect = sqlite3.connect(os.getcwd() + '/modules/YouDrawIGuess/GameInfo.db')
        cursor = connect.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS GameInfo(qqId text NOT NULL UNIQUE, state text, question text, qqgroup text)") ##创建表
        cursor.execute("insert or replace into GameInfo values (?,?,?,?)", (str(qqId), str(0), None, None))
        connect.commit()
        connect.close()

def GetYPIGSqlite3(qqId, Type):
    connect = sqlite3.connect(os.getcwd() + '/modules/YouDrawIGuess/GameInfo.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS GameInfo(qqId text NOT NULL UNIQUE, state text, question text, qqgroup text)") ##创建表
    cursor.execute("SELECT * FROM GameInfo WHERE qqId = " + "'" + str(qqId) + "'")
    ##返回获取值
    for row in cursor:
        if Type == 'state':
            info = row[1]
        elif Type == 'question':
            info = row[2]
        elif Type == 'group':
            info = row[3]
    try:
        connect.close()
        return info
    except UnboundLocalError:
        connect.close()
        return None

def WriteSignSql(qqId, info):
    connect = sqlite3.connect(os.getcwd() + '/modules/Sign/Sign.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Sign(qqId text NOT NULL UNIQUE, Signinfo text)") ##创建表
    cursor.execute("insert or replace into Sign values (?,?)", (str(qqId), str(json.dumps(info))))
    connect.commit()
    connect.close()

def GetSignSql(qqId, Type):
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


def containsAny(seq, aset):
    return True if any(i in seq for i in aset) else False