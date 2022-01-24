from typing import Set
from pydantic.utils import KeyType
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import Group, Member, GroupMessage
from graia.ariadne.model import Group, Member, MiraiSession
from graia.ariadne.message import *
from graia.ariadne.event import *
import time
import datetime


# 插件信息
__name__ = "时间机器人"
__description__ = "时间机器人"
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
    if message.asDisplay() == '咕咕几点了' or message.asDisplay() == '咕咕现在几点了' or message.asDisplay() == '咕咕现在的时间' or message.asDisplay() == '咕咕时间':
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(text="咕咕知道哦\n"),
            Plain(text="现在是 "),
            Plain(text=hour),
            Plain(text=" 点 "),
            Plain(text=minute),
            Plain(text=" 分 "),
            Plain(text=second),
            Plain(text=" 秒 ")
        ]))


