import asyncio
import os

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend, MiraiSession
import asyncio

from graia.scheduler.saya import GraiaSchedulerBehaviour, SchedulerSchema
from graia.scheduler import GraiaScheduler
from utils import load_config

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))

scheduler = GraiaScheduler(loop=bcc.loop, broadcast=bcc)
saya.install_behaviours(GraiaSchedulerBehaviour(scheduler))

configs = load_config()

app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host=configs["miraiHost"],
        verify_key=configs["ServiceVerifyKey"],
        account=configs["BotQQ"]
    )
)

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
    for module in os.listdir("modules"):
        if module in ignore:
            continue
        try:
            if os.path.isdir(module):
                saya.require(f"modules.{module}")
            else:
                saya.require(f"modules.{module.split('.')[0]}")
        except ModuleNotFoundError:
            pass

app.launch_blocking()

try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()
