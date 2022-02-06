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


saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name("choujiang")
channel.author("帝王圣鸽")
channel.description("抽奖")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def fake_forward(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if message.asDisplay() == "抽奖":
        member_list = await app.getMemberList(group)
        random_member: Member = random.choice(member_list)
        people = MessageChain.create([At(random_member)])
        await app.sendGroupMessage(group, people)