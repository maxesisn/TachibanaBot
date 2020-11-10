import random

from nonebot import on_command

from hoshino import R, Service, priv, util
from hoshino.config.__bot__ import SUPERUSERS
import re


# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'), only_to_me=True)
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')

@on_command('echo',only_to_me=False)
async def chat_echo(session):
    CQCode=session.current_arg.strip()
    if not CQCode:
        return
    else:
        if session.event.user_id not in SUPERUSERS:
            session.finish("宁也配用echo？")
        else:
            CQCode = CQ_trans(CQCode)
            await session.finish(CQCode)

def CQ_trans(cqcode:str) -> str:
    CQcode = cqcode
    CQcode = CQcode.replace('&amp;','&')
    CQcode = CQcode.replace('&#91;','[')
    CQcode = CQcode.replace('&#93;',']')
    return CQcode

sv = Service('chat', visible=False)

@sv.on_fullmatch('沙雕机器人')
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(〒︿〒)')


@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, R.img('laopo.jpg').cqcode)
    else:
        await bot.send(ev, 'mua~')


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '你给我滚！', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '笨蛋~', at_sender=True)


@sv.on_fullmatch('来点星奏')
async def seina(bot, ev):
    await bot.send(ev, R.img('星奏.png').cqcode)


@sv.on_fullmatch(('我有个朋友说他好了', '我朋友说他好了', ))
async def ddhaole(bot, ev):
    await bot.send(ev, '那个朋友是不是你弟弟？')
    await util.silence(ev, 30)


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


# ============================================ #


@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)


@sv.on_keyword(('会战'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.02:
        await bot.send(ctx, R.img('我的天啊你看看都几度了.jpg').cqcode)


@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)

nyb_player = f'''{R.img('newyearburst.gif').cqcode}
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()

@sv.on_keyword(('春黑', '新黑'))
async def new_year_burst(bot, ev):
    if random.random() < 0.02:
        await bot.send(ev, nyb_player)

@sv.on_rex(r'^给我(\d+\.?\d*)块')
@sv.on_rex(r'^我想要(\d+\.?\d*)块')
async def chat_alipay(bot, ev):
    match = ev['match']
    ali_money = match.group(1)
    await bot.send(ev, f'[CQ:record,file=https://mm.cqu.cc/share/zhifubaodaozhang/?money={ali_money}]')


@sv.on_prefix('不许')
async def chat_buxv(bot, ev):
    m = ev.message
    await bot.send(ev, f'不许不许{m}')


@sv.on_prefix('禁止')
async def chat_jinzhi(bot, ev):
    m = ev.message
    await bot.send(ev, f'禁止禁止{m}')


@sv.on_prefix(('戳他', '戳她', '戳它'))
async def chat_poke(bot, ev):
    qq_nums_raw = str(ev.message)
    qq_nums = re.findall(r'[1-9][0-9]{4,}', qq_nums_raw)
    for qq in qq_nums:
        await bot.send(ev, f'[CQ:poke,qq={qq}]')


@sv.on_prefix('戳我')  # 后期会整合成一个，加一点复杂的新功能，现在先这么用
async def chat_poke_self(bot, ev):
    await bot.send(ev, f'[CQ:poke,qq={ev.user_id}]')


@sv.on_prefix(('说：', '说:'))
async def chat_speak(bot, ev):
    await bot.send(ev, f'[CQ:tts,text={ev.message}]')


@sv.on_keyword(('给点礼物', '我也要礼物'))
async def chat_gift(bot, ev):
    await bot.send(ev, f'[CQ:gift,qq={ev.user_id},id={random.randint(0,8)}]')


@sv.on_keyword(('色图', '涩图'),only_to_me=True)
async def chat_setu(bot, ev):
    if ev.raw_message.startswith('橘小姐'):
        pass
    else:
        await bot.send(ev, R.img('no-H.JPG').cqcode)