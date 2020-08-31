import os
import urllib
import time

import aiohttp
from hoshino import Service
import datetime
import json
import re
from .exception import ServerError

svtw = Service('pcr-calender-tw', bundle='pcr日程', help_='台服日程')
svbl = Service('pcr-calender-bili', bundle='pcr日程', help_='B服日程')
svjp = Service('pcr-calender-jp', bundle='pcr日程', help_='日服日程')

async def calen_poller(region):
    event_source = f"http://toolscdn.yobot.win/calender/{region}.json"
    async with aiohttp.request("GET", url=event_source) as response:
        if response.status != 200:
            raise ServerError(f"服务器状态错误：{response.status}")
        res = response.text()
    events = json.load(res)
    for e in events:
        start_match_time = e["start_time"]
        start_time_stamp = time.mktime(time.strptime(start_match_time, "%Y/%m/%d %H:%M:%S"))
        if int(time.time())>start_time_stamp:
            end_match_time = e["end_time"]
            end_time_stamp = time.mktime(time.strptime(end_match_time, "%Y/%m/%d %H:%M:%S"))
            if int(time.time())<end_time_stamp:
                eventName=e['name'].encode('unicode_escape')
                return eventName

@svbl.on_fullmatch('B服日程')
async def calen_bili(bot,ev):
    await bot.send(ev,await calen_poller('cn'))
    return

@svtw.on_fullmatch('台服日程')
async def calen_tw(bot,ev):
    await calen_poller('tw')
    return

@svjp.on_fullmatch('日服日程')
async def calen_jp(bot,ev):
    await calen_poller('jp')
    return