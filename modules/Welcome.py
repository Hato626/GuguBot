from pydantic.utils import KeyType
from graia.saya import Saya, Channel

from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.mirai import MemberJoinEvent

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


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def group_message_listener(
    app: Ariadne,
    sender: Member,
    event: MemberJoinEvent,
    group: Group
):
    if group.id == 984392483:
        await app.sendGroupMessage(group, MessageChain.create([
            At(sender.id),
            Plain(text="欢迎来到镇守府，一起让Kekon变成称职的提督吧(*/ω＼*)")
        ]))
        await app.sendGroupMessage(group, MessageChain.create([
            Image.fromLocalFile('/mnt/file/SetuSql/Welcome.gif')
        ]))