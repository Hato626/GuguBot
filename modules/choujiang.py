
from datetime import datetime
import random
import asyncio
import aiohttp
import re

from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage, TempMessage
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At

from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from torch import per_channel_affine
 


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



        


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def fake_forward(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if message.asDisplay() == "抽奖":
        rangenum = random.randint(1,600)
        d,h,m,s =changetime(rangenum)
        RealTime =  m + '分' + s + '秒'
        await app.muteMember(group.id, member.id, rangenum)
        MessageChainA = MessageChain.create([At(member.id),Plain("\n已中奖\n----------------\n"),Plain(RealTime)])
        await app.sendGroupMessage(group, MessageChainA)


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