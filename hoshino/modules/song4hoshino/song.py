from nonebot import MessageSegment
from hoshino import Service
import requests

sv=Service("song",help_="点歌服务",enable_on_default=False)

@sv.on_prefix("点歌")
async def song(bot,ev):
    song_name=ev.message
    if not song_name:
        await bot.send("请补全歌曲名再点歌！")
        return
    
    url=f"http://localhost:3200/getSearchByKey?key={song_name}&catZhida=0"
    r=requests.get(url)
    data=r.json()
    song_id=data["response"]["data"]["song"]["list"][0]["id"]
    song_message=f'[CQ:music,type=qq,id={song_id}]'
    await bot.send(ev,song_message)
