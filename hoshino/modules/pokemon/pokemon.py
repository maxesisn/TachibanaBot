import os
import random
from re import match
import re
import sqlite3
import hoshino
from hoshino import Service
from hoshino.typing import *

sv = Service('pokemon', enable_on_default=False, help_='宝可梦（缓慢建设中）')

@sv.on_fullmatch("旅行")
async def poke_travel(bot,ev):
    
    return

@sv.on_fullmatch("我现在在哪")
async def poke_whereami():
    return

@sv.on_fullmatch("捕捉")
async def poke_catch():
    return

@sv.on_prefix('对战')
async def poke_fight(bot, ev: CQEvent):
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
    return
            
@sv.on_fullmatch("查看对战列表")
async def poke_check_fight_list():
    return

@sv.on_fullmatch("查看电脑")
async def poke_check_storge():
    return

@sv.on_rex(re.compile(r'^用(?P<pokeA>.+)换掉(?P<pokeB>.+)$'),re.I)
async def poke_exchange(bot,ev):
    match = ev['match']
    if s := match.group('pokeA'):
        pokeA=s
        if s := match.group('pokeB'):
            pokeB=s
    else:
        print ("用啥换啥？")
    return

@sv.on_fullmatch("进入友好商店")
async def poke_store():
    return

@sv.on_rex(r'^我要买(?P<buyBallNum>\d{1,2})个精灵球$')
async def poke_buyBall(bot,ev):
    buyBallNum=0
    match = ev['match']
    if s := match.group('pokeA'):
        buyBallNum=int(s)
    return

@sv.on_fullmatch("宝可梦帮助")
async def poke_help():
    return