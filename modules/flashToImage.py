from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, FlashImage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import Group, Member, GroupMessage

saya = Saya.current()
channel = Channel.current()

channel.name("FlashImageCatcher")
channel.author("SAGIRI-kawaii")
channel.description("闪照转换插件，发送闪照自动转换")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def flash_image_catcher(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if result := await FlashImageCatcherHandler.handle(app, message, group, member):
        await app.sendGroupMessage(group, result)


class FlashImageCatcherHandler():
    __name__ = "FlashImageCatcher"
    __description__ = "闪照转换插件"
    __usage__ = "发送闪照自动转换"

    async def handle(app: Ariadne, message: MessageChain, group: Group, member: Member):
        if message.has(FlashImage):
            return MessageChain.create([message[FlashImage][0].toImage()])
