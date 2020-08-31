import random
import re
import string
from hashlib import md5
from time import time
from urllib.parse import quote_plus

import aiohttp

from nonebot import get_bot
from hoshino import Service, priv as Priv
#from hoshino.service import Service, Privilege as Priv
sv = Service('tencent_ai',manage_priv=Priv.ADMIN, enable_on_default=True)

try:
    import ujson as json
except ImportError:
    import json


bot = get_bot()
cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
salt = None

################
# 请修改
app_id = '2139028130'
app_key = 'eplS4I04wCevp22k'
################


def getReqSign(params: dict) -> str:
    hashed_str = ''
    for key in sorted(params):
        hashed_str += key + '=' + quote_plus(params[key]) + '&'
    hashed_str += 'app_key='+app_key
    sign = md5(hashed_str.encode())
    return sign.hexdigest().upper()


def rand_string(n=8):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


@sv.on_message('group')
async def ai_reply(bot, context):
    if not random.randint(1,100) <= 1:#拙劣的概率开关
        return

    msg = str(context['message'])
    if msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        return

    text = re.sub(cq_code_pattern, '', msg).strip()
    if text == '':
        return

    global salt
    if salt is None:
        salt = rand_string()
    session_id = md5((str(context['user_id'])+salt).encode()).hexdigest()

    param = {
        'app_id': app_id,
        'session': session_id,
        'question': text,
        'time_stamp': str(int(time())),
        'nonce_str': rand_string(),
    }
    sign = getReqSign(param)
    param['sign'] = sign

    async with aiohttp.request(
        'POST',
        'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat',
        params=param,
    ) as response:
        code = response.status
        if code != 200:
            raise ValueError(f'bad server http code: {code}')
        res = await response.read()
        #print (res)
    param = json.loads(res)
    if param['ret'] != 0:
        raise ValueError(param['msg'])
    reply = param['data']['answer']
    await bot.send(context, reply,at_sender=False)
    #return {'reply': reply, 'at_sender': False}
