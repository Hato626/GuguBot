from datetime import datetime

from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage
from graia.ariadne.message.element import ForwardNode, Image, Plain, Forward, At


saya = Saya.current()
channel = Channel.current()

channel.name("FakeForward")
channel.author("SAGIRI-kawaii")
channel.description("一个生成转发消息的插件，发送 '/FakeNews [@目标] [内容]' 即可")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def fake_forward(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if result := await FakeForward.handle(app, message, group, member):
        await app.sendGroupMessage(group, result)


class FakeForward():
    __name__ = "FakeForward"
    __description__ = "转发消息生成器"
    __usage__ = "None"

    async def handle(app: Ariadne, message: MessageChain, group: Group, member: Member):
        if message.asDisplay().startswith("FakeNews "):
            content = "".join(i.text for i in message.get(Plain))[9:]
            if not message.has(At):
                messageList = "".join(i.text for i in message.get(Plain)).split()
                qqId = messageList[1]
                messageStr = messageList[2]
                try:
                    forward_nodes = [
                        ForwardNode(
                            senderId=int(qqId),
                            time=datetime.now(),
                            #senderName=(await app.getStranger(qqId)).nickname,
                            messageChain=MessageChain.create(Plain(text=messageStr)),
                            )
                        ]
                    return MessageChain.create(Forward(nodeList=forward_nodes))
                except:
                    return MessageChain.create([Plain(text="未指定目标!")])
            else:
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
