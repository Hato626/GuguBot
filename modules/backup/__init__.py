from pydantic.utils import KeyType
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, FlashImage, Image, At, Quote
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import *
from graia.ariadne.message.element import Source
from graia.ariadne.event.mirai import *
import os
import ssl
import sqlite3
import re
import itertools
 
ssl._create_default_https_context = ssl._create_unverified_context


# 插件信息
__name__ = "MessagePrinter"
__description__ = "打印收到的消息"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送消息即可触发"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)



@channel.use(ListenerSchema(listening_events=[GroupRecallEvent]))
async def group_recall_listener(
    app: Ariadne,
    sender: Member,
    group: Group,
    event: GroupRecallEvent
):
    messageid = event.messageId
    MessageStr,authorId = GetSqlite3(messageid)
    if MessageStr != None and authorId != None:
        MessageListA = re.findall('\[.*?\]', MessageStr) ##mirai码列表
        MessageListB = re.split('\[.*?\]', MessageStr) ##文本列表,第一个参数为空

        ##判断是否存在mirai码
        if MessageListA == []:
            MessageListA = ['aaaaaa']
        ##判断mirai码列表是否判断错误
        for i in MessageListA:
            MiraiStr = str(i[1:-1])
            MiraiList = MiraiStr.split(":")
            if MiraiList[0] != 'mirai':
                MessageStr = MessageStr.replace(i,'')
        
        ##删除文本列表第一个空元素
        MessageListB.pop(0)


        ##判断是否有Voice元素
        for i in MessageListA:
            MiraiStr = str(i[1:-1])
            MiraiList = MiraiStr.split(":")
            if MiraiList[0] == 'voice':
                VoiceState = True
                VoiceMessageId = str(MessageListA[0][1:-1]).split(":")[2].split(",")[0]
                VoiceGroupMesage = await app.getMessageFromId(VoiceMessageId)
                VoiceMessageChain = VoiceGroupMesage.messageChain
            else:
                VoiceState = False
        
        ##判断是否有Quote元素
        for i in MessageListA:
            MiraiStr = str(i[1:-1])
            MiraiList = MiraiStr.split(":")
            if MiraiList[0] == 'quote':
                QuoteState = True
                MessageStr = MessageStr.replace(i,'')
                MessageListA.remove(i)
                QuoteMessageId = MiraiList[2].split(',')[0]
                QuoteGroupMesage = await app.getMessageFromId(QuoteMessageId)
                QuoteSenderId = QuoteGroupMesage.sender.id
                QuoteSenderName = QuoteGroupMesage.sender.name
                QuoteMessageChain = QuoteGroupMesage.messageChain
            else:
                QuoteState = False

        ##发送
        if sender.permission.value == 'MEMBER' and IsSendGroup(sender.group.id):
            if QuoteState == True:
                MessageChainA = MessageChain.create([At(authorId),Plain("撤回了一条信息\n----------------\n")])
                MessageChainB = MessageChain.create([Plain("引用了"),At(QuoteSenderId),Plain("的信息("),Plain(QuoteMessageId),Plain("):\n")])
                MessageChainC = MessageChain.asSendable(QuoteMessageChain)
                MessageChainD = MessageChain.create([Plain("\n----------------\n")])
                MessageChainE = MessageChain.asSendable(MessageChain.fromPersistentString(MessageStr))
                MessageChainF = MessageChain.create(list(itertools.chain(MessageChainA, MessageChainB, MessageChainC, MessageChainD, MessageChainE)))
                await app.sendGroupMessage(group, MessageChainF)
            elif VoiceState == True:
                MessageChainA = MessageChain.create([At(authorId),Plain("撤回了一条语言信息")])
                MessageChainB = MessageChain.asSendable(VoiceMessageChain)
                await app.sendGroupMessage(group, MessageChainA)
                await app.sendGroupMessage(group, MessageChainB)
            else:
                messageid = event.messageId
                message,authorId = GetSqlite3(messageid)
                MessageChainA = MessageChain.create([At(authorId),Plain("\n撤回了一条消息\n----------------\n")])
                MessageChainB = MessageChain.asSendable((MessageChain.fromPersistentString(message)))
                MessageChainC = MessageChain.create(list(itertools.chain(MessageChainA, MessageChainB)))
                await app.sendGroupMessage(group, MessageChainC)
        else:
            print("判断为管理员撤回，不执行操作")
    else:
        MessageChainA = MessageChain.create([Plain("好像有人撤回了一条信息，但我数据库中找不到QAQ")])
        await app.sendGroupMessage(group, MessageChainA)
        print("未从数据库获取到缓存")

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    WriteSqlite3(message[Source][0].id, sender.id, group.id, message[Source][0].time, message.asPersistentString(), sender.name)
    



def IsSendGroup(groupid):
    group = [371815444,956162597]
    if groupid in group:
        return True
    else:
        return False

def WriteSqlite3(messageId, authorId, groupId, time, message, authorName):
    connect = sqlite3.connect(os.getcwd() + '/modules/backup/backup.db')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS message(messageId text,authorId text,groupId text,time text,message text,authorName text)") ##创建表
    cursor.execute("insert into message values (?,?,?,?,?,?)", (messageId, authorId, groupId, time, message, authorName))
    connect.commit()
    connect.close()

def GetSqlite3(messageId):
    connect = sqlite3.connect(os.getcwd() + '/modules/backup/backup.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM message WHERE messageId = " + "'" + str(messageId) + "'")
    for row in cursor:
        message = row[4]
        authorId = int(row[1])
    try:
        connect.close()
        return message,authorId
    except UnboundLocalError:
        connect.close()
        return None,None
