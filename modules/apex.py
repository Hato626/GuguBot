from datetime import datetime
import random
import asyncio
import aiohttp
import re
import urllib
import urllib.request
import urllib.parse
import json

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
channel.author("Hato")
channel.description("一个生成转发消息的插件，发送 '/FakeNews [@目标] [内容]' 即可")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def fake_forward(app: Ariadne, message: MessageChain, group: Group, member: Member):
    if message.asDisplay().startswith("apexmap"):
        MapInfo = await GetInfo.GetMapInfo()
        await SendMessage.SendMaprInfoMessage(app,group.id,MapInfo)
    elif message.asDisplay().startswith("apex "):
        playerid = "".join(i.text for i in message.get(Plain))[5:]
        try:
            playerinfo = await GetInfo.GetPlayerInfo(playerid)
            await SendMessage.SendPlayerInfoMessage(app,group.id,playerinfo)
        except:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="呜呜，咕咕找不到这个人的信息\n可能是输入的名称不是origin昵称?")]))


class GetInfo:
    ##通过API获取用户名
    async def GetPlayerInfo(playerid):
         #Api地址
        ApiUrl = 'https://api.mozambiquehe.re/bridge?version=5&platform=PC&auth=FsKmkWPMRJlOEmW8H3ZN&player='
        GetUrl = ApiUrl + urllib.parse.quote(str(playerid))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}
        url = urllib.request.Request(url=GetUrl, headers=headers)
        response = urllib.request.urlopen(url)
        info = json.loads(response.read().decode("utf-8"))
        return info

    async def GetMapInfo():
        GetUrl = "https://api.mozambiquehe.re/maprotation?version=2&auth=FsKmkWPMRJlOEmW8H3ZN"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}
        url = urllib.request.Request(url=GetUrl, headers=headers)
        response = urllib.request.urlopen(url)
        info = json.loads(response.read().decode("utf-8"))
        return info


class SendMessage:
    async def SendPlayerInfoMessage(app,group,info):
        messagechain = MessageChain.create([
            Plain(text="名称: "), Plain(text=info["global"]["name"]), Plain(text="\n"),
            Plain(text="等级: "), Plain(text=info["global"]["level"]), Plain(text="\n"),
            Plain(text="--------排位--------"), Plain(text="\n"),
            Plain(text="段位: "), Plain(text=info["global"]["rank"]["rankName"]), Plain(text="\n"),
            Plain(text="分数: "), Plain(text=info["global"]["rank"]["rankScore"]), Plain(text="\n"),
            Plain(text="--------竞技场--------"), Plain(text="\n"),
            Plain(text="段位: "), Plain(text=info["global"]["arena"]["rankName"]), Plain(text="\n"),
            Plain(text="分数: "), Plain(text=info["global"]["arena"]["rankScore"]), Plain(text="\n"),
            Plain(text="--------状态--------"), Plain(text="\n"),
            Plain(text="在线状态: "), Plain(text=await changestate.online(info["realtime"]["isOnline"])), Plain(text="\n"),
            Plain(text="游戏状态: "), Plain(text=await changestate.gameing(info["realtime"]["isOnline"])), Plain(text="\n"),
            Plain(text="队伍状态: "), Plain(text=await changestate.partyFull(info["realtime"]["partyFull"])),
            ])
        await app.sendGroupMessage(group, messagechain)

    async def SendMaprInfoMessage(app,group,info):
        messagechain = MessageChain.create([
            Plain(text="--------匹配--------"), Plain(text="\n"),
            Plain(text="当前地图: "), Plain(text=info["battle_royale"]["current"]["map"]), Plain(text="\n"),
            Plain(text="剩余时间: "), Plain(text=info["battle_royale"]["current"]["remainingTimer"]), Plain(text="\n"),
            Plain(text="下一轮换: "), Plain(text=info["battle_royale"]["next"]["map"]), Plain(text="\n"),
            Plain(text="--------竞技场--------"), Plain(text="\n"),
            Plain(text="当前地图: "), Plain(text=info["arenas"]["current"]["map"]), Plain(text="\n"),
            Plain(text="剩余时间: "), Plain(text=info["arenas"]["current"]["remainingTimer"]), Plain(text="\n"),
            Plain(text="下一轮换: "), Plain(text=info["arenas"]["next"]["map"]), Plain(text="\n"),
            Plain(text="--------排位--------"), Plain(text="\n"),
            Plain(text="当前地图: "), Plain(text=info["ranked"]["current"]["map"]), Plain(text="\n"),
            Plain(text="下一轮换: "), Plain(text=info["ranked"]["next"]["map"]), Plain(text="\n"),
            Plain(text="------排位竞技场------"), Plain(text="\n"),
            Plain(text="当前地图: "), Plain(text=info["arenasRanked"]["current"]["map"]), Plain(text="\n"),
            Plain(text="剩余时间: "), Plain(text=info["arenasRanked"]["current"]["remainingTimer"]), Plain(text="\n"),
            Plain(text="下一轮换: "), Plain(text=info["arenasRanked"]["next"]["map"])
            ])
        await app.sendGroupMessage(group, messagechain)



class changestate:
    async def online(state):
        if state == 0:
            return "离线"
        elif state == 1:
            return "在线"
        else:
            return "未知状态"

    async def gameing(state):
        if state == 0:
            return "未在游戏"
        elif state == 1:
            return "游戏中"
        else:
            return "未知状态"

    async def partyFull(state):
        if state == 0:
            return "空闲"
        elif state == 1:
            return "已满"
        else:
            return "未知状态"