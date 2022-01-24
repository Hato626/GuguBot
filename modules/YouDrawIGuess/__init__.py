from typing import Set
from pydantic.utils import KeyType
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage, FriendMessage, Friend, TempMessage
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
import os
import sqlite3


# 插件信息
__name__ = "你画我猜"
__description__ = "你画我猜"
__author__ = "帝王圣鸽"
__usage__ = "发送消息即可触发"


saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法:{__usage__}")
channel.author(__author__)

UseMoney = True
OnePointUseMoney = 4
ecoType = '痕币'



##监听群聊消息并截断
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    ##创建游戏处理
    if message.asDisplay() == '你画我猜':
        GameState = GetSqlite3(sender.id, 'state')
        if GameState == str(0) or GameState == None:
            if UseMoney == True:
                await app.sendGroupMessage(group, MessageChain.create([
                        At(sender.id),
                        Plain(text="是否创建一场你画我猜,这将消耗你 "),
                        Plain(text=OnePointUseMoney),
                        Plain(text=" 枚"),
                        Plain(text=ecoType),
                        Plain(text="(是/否)"),
                    ]))
                GroupMessage = await inc.wait(YesorNoWaiter)
                MessageDisPlay = GroupMessage.asDisplay()
                if MessageDisPlay == '是' or MessageDisPlay == 'Y' or MessageDisPlay == '/confirm' or MessageDisPlay == 'y' or MessageDisPlay == 'yes':
                    Money = GetMoney(sender.id)
                    if Money - OnePointUseMoney >= 0:
                        CreatNewGame(sender.id, group.id)
                        SetMoney(sender.id, 'reduce', OnePointUseMoney)
                        await app.sendGroupMessage(group, MessageChain.create([
                            At(sender.id),
                            Plain(text="已创建一场你画我猜, 请与机器人私聊答案\n"),
                            Plain(text="私聊方式: 临时聊天/加好友 (若临时聊天无反应时加好友)\n"),
                            Plain(text="创建者发送<结束/取消/终止>可结束本次游戏")
                        ]))
                    else:
                        await app.sendGroupMessage(group, MessageChain.create([
                            At(sender.id),
                            Plain(text=ecoType),
                            Plain(text="不足\n"),
                            Plain(text="您只有 "),
                            Plain(text=Money),
                            Plain(text=" 枚"),
                            Plain(text=ecoType),
                        ]))
                else:
                    await app.sendGroupMessage(group, MessageChain.create([
                        At(sender.id),
                        Plain(text="已取消"),
                    ]))
            else:
                CreatNewGame(sender.id, group.id)
                await app.sendGroupMessage(group, MessageChain.create([
                    At(sender.id),
                    Plain(text="已创建一场你画我猜, 请与机器人私聊答案\n"),
                    Plain(text="私聊方式: 临时聊天/加好友 (若临时聊天无反应时加好友)\n"),
                    Plain(text="创建者发送<结束/取消/终止>可结束本次游戏")
                ]))
        ##如果游戏状态为1，即创建了游戏但没有告诉机器人答案
        elif GameState == str(1):
            await app.sendGroupMessage(group, MessageChain.create([
                At(sender.id),
                Plain(text="你已经创建了一场你画我猜,请与机器人私聊答案\n"),
                Plain(text="或者发送<结束/取消/终止>可结束本次游戏")
            ]))
        elif GameState == str(2):
            await app.sendGroupMessage(group, MessageChain.create([
                At(sender.id),
                Plain(text="你已经创建一场你画我猜,请等待回答者回答\n"),
                Plain(text="回答者需要发送 <@创建者><答案>即可回答问题\n"),
                Plain(text="发送<结束/取消/终止>可结束本次游戏\n")
            ]))
    ##回答问题处理
    if message.has(At):
        targetId = message.get(At)[0].target
        state = GetSqlite3(targetId, 'state')
        if state == str(2):
            answer = message.get(Plain)[0].text
            state = GetSqlite3(targetId, 'state')
            question = GetSqlite3(targetId, 'question')
            Mastergroup = GetSqlite3(targetId, 'group')
            if answer.startswith(' '):answer = answer[1:]
            if answer.endswith(' '):answer = answer[:-1]
            if str(group.id) == str(Mastergroup):
                if answer == question:
                    if UseMoney == True:
                        await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="恭喜猜出本次答案，获得 2 个"),Plain(text=ecoType)]))
                        #await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="恭喜猜出本次答案")]))
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text="本次游戏结束")]))
                        ##更新金币数据库
                        SetMoney(sender.id, 'add', 2)
                        EndGame(targetId)
                    else:
                        await app.sendGroupMessage(group, MessageChain.create([At(sender.id),Plain(text="恭喜猜出本次答案")]))
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text="本次游戏结束")]))
                        EndGame(targetId)
                else:
                    await app.sendGroupMessage(group, MessageChain.create([Plain(text="回答错误")]))
    ##取消问题处理
    if message.asDisplay() == '取消' or message.asDisplay() == '结束' or message.asDisplay() == '终止':
        if GetSqlite3(sender.id, 'state') != str(0) and GetSqlite3(sender.id, 'state') != None:
            EndGame(sender.id)
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="成功取消游戏进程, 本次游戏结束")]))
            if UseMoney == True:
                SetMoney(sender.id, 'add', OnePointUseMoney - 1)
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(text="已退还 "),
                    Plain(text=OnePointUseMoney - 1),
                    Plain(text=" 枚"),
                    Plain(text=ecoType)
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                    Plain(text="你没有创建游戏进程"),
                ]))


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Friend,
):
    GameState = GetSqlite3(sender.id, 'state')
    if GameState == str(1):
        group = GetSqlite3(sender.id, 'group')
        WriteSqlite3(sender.id, 'question', message.get(Plain)[0].text)
        await app.sendFriendMessage(sender, MessageChain.create([
            Plain(text="提交答案成功\n"),
            Plain(text="请在群中以涂鸦形式绘制图片或以其他形式表达该主题\n\n"),
            Plain(text="发送<结束/取消/终止>可结束本次游戏")
        ]))
        await app.sendGroupMessage(group, MessageChain.create([
            At(sender.id),
            Plain(text="本次答案为 "),
            Plain(text=len(GetSqlite3(sender.id, 'question'))),
            Plain(text=" 个字, 请等待创建者绘制图片\n"),
            Plain(text="回答者需要发送 <@创建者><答案> 来猜答案"),
        ]))
    if GameState == str(2):
        await app.sendFriendMessage(sender, MessageChain.create([
            Plain(text="你已经提交了答案\n"),
            Plain(text="发送<结束/取消/终止>可结束本次游戏")
        ]))



@channel.use(ListenerSchema(listening_events=[TempMessage]))
async def temp_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    GameState = GetSqlite3(sender.id, 'state')
    if GameState == str(1):
        WriteSqlite3(sender.id, 'question', message.get(Plain)[0].text)
        await app.sendTempMessage(group, sender, MessageChain.create([
            Plain(text="提交答案成功\n"),
            Plain(text="请在群中以涂鸦形式绘制图片或以其他形式表达该主题\n\n"),
            Plain(text="发送<结束/取消/终止>可结束本次游戏")
        ]))
        await app.sendGroupMessage(group, MessageChain.create([
            At(sender.id),
            Plain(text="本次答案为 "),
            Plain(text=len(GetSqlite3(sender.id, 'question'))),
            Plain(text=" 个字, 请等待创建者绘制图片\n"),
            Plain(text="回答者需要发送 <@创建者><答案> 来猜答案"),
        ]))
    if GameState == str(2):
        await app.sendTempMessage(group, sender, MessageChain.create([Plain(text="你已经提交了答案\n"),
            Plain(text="发送<结束/取消/终止>可结束本次游戏")
        ]))
    


@Waiter.create_using_function([GroupMessage])
async def YesorNoWaiter(waiter_group: Group, waiter_member: Member, waiter_message: MessageChain):
    print(waiter_member.id)
    return waiter_message



def WriteSqlite3(qqId, Type, info):
    if Type == 'CreatNewGame':
        connect = sqlite3.connect(os.getcwd() + '/modules/YouDrawIGuess/GameInfo.db')
        cursor = connect.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS GameInfo(qqId text NOT NULL UNIQUE, state text, question text, qqgroup text)") ##创建表
        cursor.execute("insert or replace into GameInfo values (?,?,?,?)", (str(qqId), str(1), None, str(info)))
        connect.commit()
        connect.close()
    if Type == 'question':
        group = GetSqlite3(qqId, 'group')
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

def GetSqlite3(qqId, Type):
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
        NewMoney = OldMoney + quantity
    elif Type == 'reduce':
        NewMoney = OldMoney - quantity
    connect = sqlite3.connect(os.getcwd() + '/modules/Money.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Money(qqId text NOT NULL UNIQUE, money text)") ##创建表
    cursor.execute("insert or replace into Money values (?,?)", (str(qqId), str(NewMoney)))
    connect.commit()
    connect.close()




def CreatNewGame(qqId, group):
    WriteSqlite3(qqId, 'CreatNewGame', group)

def EndGame(qqId):
    WriteSqlite3(qqId, 'EndGame', None)

