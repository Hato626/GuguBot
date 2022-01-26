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




saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name("FakeForward")
channel.author("SAGIRI-kawaii")
channel.description("一个生成转发消息的插件，发送 '/FakeNews [@目标] [内容]' 即可")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def fake_forward(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if message.asDisplay().startswith("FakeNews "):
        result = await FakeForward.handle(app, message, group, member)
        await app.sendGroupMessage(group, result)
    elif message.asDisplay() == 'FakeNews':
        GroupMessage = await WaitMessageClass.handle(app, message, group, member)
        if GroupMessage.asDisplay() != '等待超时，进程退出':
            result = await FakeForward.ForwardChain(app, GroupMessage, group, member)
            await app.sendGroupMessage(group, result)
        else:
            app.sendGroupMessage(group, GroupMessage)


class FakeForward():
    __name__ = "FakeForward"
    __description__ = "转发消息生成器"
    __usage__ = "None"

    async def handle(app: Ariadne, message: MessageChain, group: Group, member: Member):
        if message.asDisplay().startswith("FakeNews "):
            content = "".join(i.text for i in message.get(Plain))[9:]
            if not message.has(At):
                # messageList = "".join(i.text for i in message.get(Plain)).split()
                # qqId = messageList[1]
                # messageStr = messageList[2]
                # try:
                #     forward_nodes = [
                #         ForwardNode(
                #             senderId=int(qqId),
                #             time=datetime.now(),
                #             #senderName=(await app.getStranger(qqId)).nickname,
                #             messageChain=MessageChain.create(Plain(text=messageStr)),
                #             )
                #         ]
                #     return MessageChain.create(Forward(nodeList=forward_nodes))
                # except:
                return MessageChain.create([Plain(text="未指定目标!")])
            sender = message.get(At)[0]
            forward_nodes = [
                ForwardNode(
                    senderId=sender.target,
                    time=datetime.now(),
                    senderName=(await app.getMember(group, sender.target)).name,
                    messageChain=MessageChain.create(Plain(text=content)),
                )
            ]
            return MessageChain.create(Forward(nodeList=forward_nodes))


    async def ForwardChain(app: Ariadne, message: MessageChain, group: Group, member: Member):
        MessageChainStr = message.asPersistentString()
        MessageChainStr = MessageChainStr.replace('\\n','{otherline}')
        MessageChainList = MessageChainStr.split('\n')
        MessageChainDict = {}
        iv = 0
        for i in MessageChainList:
            OneLineList = i.split(':')
            if len(OneLineList) == 2:
                MessageChainDict[iv] = {'qqId': OneLineList[0], 'name' : await GetNameFromApi(OneLineList[0]), 'message' : OneLineList[1].replace('{otherline}', '\\n')}
            else:
                message = i.replace(OneLineList[0] + ':', '')
                message = message.replace('{otherline}', '\\n')
                MessageChainDict[iv] = {'qqId': OneLineList[0], 'name' : await GetNameFromApi(OneLineList[0]), 'message' : message}
            iv = iv + 1


        ##新建一个消息链
        forward_nodes=[]
        for i in MessageChainDict:
            Name = MessageChainDict[i]['name']
            qqId = MessageChainDict[i]['qqId']
            messageChain = MessageChain.fromPersistentString(MessageChainDict[i]['message'])
            Time=datetime.now()
            try:
                forward_nodes.append(
                    ForwardNode(
                        senderId=qqId,
                        time=Time,
                        senderName=Name,
                        messageChain=messageChain,
                    )
                )
            except:
                pass

        print(forward_nodes)
        return MessageChain.create(Forward(nodeList=forward_nodes))



class WaitMessageClass:
    async def handle(app: Ariadne, message: MessageChain, group: Group, member: Member):
        @Waiter.create_using_function(listening_events=[GroupMessage])
        async def MessageWaiter(waiter_group: Group, waiter_member: Member, waiter_message: MessageChain):
            if waiter_group.id == group.id and waiter_member.id == member.id:
                return waiter_message
        try:
            await app.sendMessage(group, MessageChain.create("请在30s内发送要处理的信息"))
            Message = await asyncio.wait_for(inc.wait(MessageWaiter), 30)
            return Message
        except asyncio.TimeoutError:
            return MessageChain.create([Plain(text="等待超时，进程退出")])







#Api地址
ApiUrl = 'https://api.vvhan.com/api/qq?qq='
##通过API获取用户名
async def GetNameFromApi(qqId):
    GetUrl = ApiUrl + str(qqId)
    async with aiohttp.ClientSession() as session:
        async with session.get(GetUrl) as r:
            ReturnJson = await r.json()
            if 'name' in ReturnJson:
                Name = ReturnJson['name']
            else:  
                Name = '获取失败'
            return Name