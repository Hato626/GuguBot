from pydantic.utils import KeyType
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage, FriendMessage, Friend
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At
import os
import sqlite3


# 插件信息
__name__ = "经济系统"
__description__ = "经济系统"
__author__ = "帝王圣鸽"
__usage__ = "发送消息即可触发"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法:{__usage__}")
channel.author(__author__)





@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    if message.asDisplay() == '我的痕币' or message.asDisplay() == '查询痕币':
        Money = GetMoney(sender.id, 'id')
        await app.sendGroupMessage(group, MessageChain.create([
                At(sender.id),
                Plain(text="\n经统计,您一共拥有 "),
                Plain(text=Money),
                Plain(text=" 枚痕币")
            ]))
    if message.asDisplay() == '痕币排行' or message.asDisplay() == '痕币排行榜' or message.asDisplay() == '痕币排名':
        Info = GetMoney(sender.id, 'all')
        ThisGroupMemberList = await app.memberList(group)
        ThisGroupMoneyInfo = {}
        for i in ThisGroupMemberList:
            if str(i.id) in Info:
                ThisGroupMoneyInfo[str(i.id)] = int(Info[str(i.id)])
        MoneyList = dict(sorted(ThisGroupMoneyInfo.items(), key = lambda kv:kv[1], reverse=True))
        MoneyListStr = ''
        Num = 0
        for i in MoneyList:
            if Num < 6:
                member = await app.getMember(group,int(i))
                name = member.name
                MoneyListStr = MoneyListStr + name + '(' + str(i) + ')' + ' : ' + str(MoneyList[i]) + ' 枚' + '\n'
                Num = Num + 1
            else:
                pass
        MoneyListStr = MoneyListStr[:-1]
        await app.sendGroupMessage(group, MessageChain.create([
                Plain(text=MoneyListStr)
            ]))
    
@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Friend,
):
    if message.asDisplay() == '我的痕币' or message.asDisplay() == '查询痕币':
        Money = GetMoney(sender.id, 'id')
        await app.sendFriendMessage(sender, MessageChain.create([
                Plain(text="经统计,您一共拥有 "),
                Plain(text=Money),
                Plain(text=" 枚痕币")
            ]))




def GetMoney(qqId, Type):
    connect = sqlite3.connect(os.getcwd() + '/modules/Money.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Money(qqId text NOT NULL UNIQUE, money text)") ##创建表
    if Type == 'id':
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
    elif Type == 'all':
        cursor.execute("SELECT * FROM Money")
        ##返回获取值
        info = {}
        for row in cursor:
            info[row[0]] = row[1]
        try:
            connect.close()
            return info
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
