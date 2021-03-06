import re
import time
import asyncio
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

import hoshino
from hoshino import Service, R
from hoshino.typing import *
from hoshino.util import FreqLimiter, concat_pic, pic2b64, silence

from .. import chara

sv_help = '''
[怎么拆] 接防守队角色名 查询竞技场解法
[点赞] 接作业id 评价作业
[点踩] 接作业id 评价作业
'''.strip()
sv = Service('pcr-arena', help_=sv_help, bundle='pcr查询')

from . import arena

lmt = FreqLimiter(5)

aliases = ('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', 'jjc查询')
aliases_b = tuple('b' + a for a in aliases) + tuple('B' + a for a in aliases)
aliases_tw = tuple('台' + a for a in aliases)
aliases_jp = tuple('日' + a for a in aliases)

try:
    thumb_up_i = R.img('priconne/gadget/thumb-up-i.png').open().resize((16, 16), Image.LANCZOS)
    thumb_up_a = R.img('priconne/gadget/thumb-up-a.png').open().resize((16, 16), Image.LANCZOS)
    thumb_down_i = R.img('priconne/gadget/thumb-down-i.png').open().resize((16, 16), Image.LANCZOS)
    thumb_down_a = R.img('priconne/gadget/thumb-down-a.png').open().resize((16, 16), Image.LANCZOS)
except Exception as e:
    sv.logger.exception(e)

@sv.on_prefix(aliases)
async def arena_query(bot, ev):
    await _arena_query(bot, ev, region=1)

@sv.on_prefix(aliases_b)
async def arena_query_b(bot, ev):
    await _arena_query(bot, ev, region=2)

@sv.on_prefix(aliases_tw)
async def arena_query_tw(bot, ev):
    await _arena_query(bot, ev, region=3)

@sv.on_prefix(aliases_jp)
async def arena_query_jp(bot, ev):
    await _arena_query(bot, ev, region=4)


def render_atk_def_teams(id, m, entries, border_pix=5):
    nickname = m["card"] or m["nickname"] or str(id)
    n = len(entries)
    icon_size = 64
    im = Image.new('RGBA', (5 * icon_size + 80, n * (icon_size + border_pix) - border_pix + 100), (255, 255, 255, 255))
    #使用思源黑体，debian系直接sudo apt-get install fonts-noto-cjk即可安装，其它系统好自为之
    font = ImageFont.truetype('NotoSansCJK-Regular.ttc', 16)
    draw = ImageDraw.Draw(im)
    draw.text((0,0),f'已为骑士君 @{nickname} 查询到以下进攻方案：', (0, 0, 0, 255), font)
    for i, e in enumerate(entries):
        y1 = i * (icon_size + border_pix) + 22
        y2 = y1 + icon_size
        for j, c in enumerate(e['atk']):
            icon = c.render_icon(icon_size)
            x1 = j * icon_size
            x2 = x1 + icon_size
            im.paste(icon, (x1, y1, x2, y2), icon)
        thumb_up = thumb_up_a if e['user_like'] > 0 else thumb_up_i
        thumb_down = thumb_down_a if e['user_like'] < 0 else thumb_down_i
        x1 = 5 * icon_size + 5
        x2 = x1 + 16
        im.paste(thumb_up, (x1, y1+22, x2, y1+38), thumb_up)
        im.paste(thumb_down, (x1, y1+44, x2, y1+60), thumb_down)
        draw.text((x1, y1), e['qkey'], (0, 0, 0, 255), font)
        draw.text((x1+16, y1+20), f"{e['up']}+{e['my_up']}" if e['my_up'] else f"{e['up']}", (0, 0, 0, 255), font)
        draw.text((x1+16, y1+40), f"{e['down']}+{e['my_down']}" if e['my_down'] else f"{e['down']}", (0, 0, 0, 255), font)
    draw.text((5,(icon_size + border_pix) * n + 22 + 10),'※发送"点赞/点踩"可进行评价', (0, 0, 0, 255), font)
    draw.text((5,(icon_size + border_pix) * n + 22 + 28),'※使用"b怎么拆"或"台怎么拆"可按服过滤', (0, 0, 0, 255), font)
    draw.text((5,(icon_size + border_pix) * n + 22 + 46),'Support by pcrdfans.com', (0, 0, 0, 255), font)
    return im


async def _arena_query(bot, ev: CQEvent, region: int):
    at = str(MessageSegment.at(ev.user_id))
    reply = f'[CQ:reply,id={ev.message_id}]' + at
    arena.refresh_quick_key_dic()
    uid = ev.user_id

    if not lmt.check(uid):
        await bot.finish(ev, reply+'您查询得过于频繁，请稍等片刻')
    lmt.start_cd(uid)

    # 处理输入数据
    defen = ev.message.extract_plain_text()
    defen = re.sub(r'[?？，,_]', '', defen)
    defen, unknown = chara.roster.parse_team(defen)

    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
        await bot.finish(ev, msg)
    if not defen:
        await bot.finish(ev, reply+'查询请发送"怎么拆+防守队伍"，无需+号')
    if len(defen) > 5:
        await bot.finish(ev, reply+'编队不能多于5名角色')
    if len(defen) < 5:
        await bot.finish(ev, reply+'由于数据库限制，少于5名角色的检索条件请移步pcrdfans.com进行查询')
    if len(defen) != len(set(defen)):
        await bot.finish(ev, reply+'编队中含重复角色')
    if any(chara.is_npc(i) for i in defen):
        await bot.finish(ev, reply+'编队中含未实装角色')
    if 1004 in defen:
        await bot.send(ev, reply+'\n⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称')

    # 执行查询
    sv.logger.info('Doing query...')
    res = None
    try:
        res = await arena.do_query(defen, uid, region)
    except hoshino.aiorequests.HTTPError as e:
        code = e.response["code"]
        if code == 117:
            await bot.finish(ev, "高峰期服务器限流！请前往pcrdfans.com/battle")
        else:
            await bot.finish(ev, f'code{code} 查询出错，请联系维护组调教\n请先前往pcrdfans.com进行查询', at_sender=True)
    sv.logger.info('Got response!')

    # 处理查询结果
    if res is None:
        await bot.finish(ev, '数据库未返回数据，请再次尝试查询或前往pcrdfans.com', at_sender=True)
    if not len(res):
        await bot.finish(ev, reply+'抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★\n作业上传请前往pcrdfans.com')
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    # 发送回复
    sv.logger.info('Arena generating picture...')
    m = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=ev.group_id, user_id=ev.user_id
        )
    teams = render_atk_def_teams(ev.user_id, m, res)
    teams = pic2b64(teams)
    teams = MessageSegment.image(teams)
    sv.logger.info('Arena picture ready!')
    # 纯文字版
    # atk_team = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res))

    # details = [" ".join([
    #     f"赞{e['up']}+{e['my_up']}" if e['my_up'] else f"赞{e['up']}",
    #     f"踩{e['down']}+{e['my_down']}" if e['my_down'] else f"踩{e['down']}",
    #     e['qkey'],
    #     "你赞过" if e['user_like'] > 0 else "你踩过" if e['user_like'] < 0 else ""
    # ]) for e in res]

    # defen = [ chara.fromid(x).name for x in defen ]
    # defen = f"防守方【{' '.join(defen)}】"

    #msg = [
        # defen,
        #f'已为骑士{at}查询到以下进攻方案：',
        #str(teams),
        # '作业评价：',
        # *details,
        #'※发送"点赞/点踩"可进行评价'
    #]
    #if region == 1:
    #    msg.append('※使用"b怎么拆"或"台怎么拆"可按服过滤')
    #msg.append('Support by pcrdfans_com')

    sv.logger.debug('Arena sending result...')
    await bot.send(ev, reply+str(teams))
    sv.logger.debug('Arena result sent!')


# @sv.on_prefix('点赞')
async def arena_like(bot, ev):
    await _arena_feedback(bot, ev, 1)


# @sv.on_prefix('点踩')
async def arena_dislike(bot, ev):
    await _arena_feedback(bot, ev, -1)


rex_qkey = re.compile(r'^[0-9a-zA-Z]{5}$')
async def _arena_feedback(bot, ev: CQEvent, action: int):
    action_tip = '赞' if action > 0 else '踩'
    qkey = ev.message.extract_plain_text().strip()
    if not qkey:
        await bot.finish(ev, f'请发送"点{action_tip}+作业id"，如"点{action_tip}ABCDE"，不分大小写', at_sender=True)
    if not rex_qkey.match(qkey):
        await bot.finish(ev, f'您要点{action_tip}的作业id不合法', at_sender=True)
    try:
        await arena.do_like(qkey, ev.user_id, action)
    except KeyError:
        await bot.finish(ev, '无法找到作业id！您只能评价您最近查询过的作业', at_sender=True)
    await bot.send(ev, '感谢您的反馈！', at_sender=True)


@sv.on_command('arena-upload', aliases=('上传作业', '作业上传', '上傳作業', '作業上傳'))
async def upload(ss: CommandSession):
    atk_team = ss.get('atk_team', prompt='请输入进攻队+5个表示星级的数字+5个表示专武的0/1 无需空格')
    def_team = ss.get('def_team', prompt='请输入防守队+5个表示星级的数字+5个表示专武的0/1 无需空格')
    if 'pic' not in ss.state:
        ss.state['pic'] = MessageSegment.image(pic2b64(concat_pic([
            chara.gen_team_pic(atk_team),
            chara.gen_team_pic(def_team),
        ])))
    confirm = ss.get('confirm', prompt=f'{ss.state["pic"]}\n{MessageSegment.at(ss.event.user_id)}确认上传？\n> 确认\n> 取消')
    # TODO: upload
    await ss.send('假装上传成功了...')


@upload.args_parser
async def _(ss: CommandSession):
    if ss.is_first_run:
        await ss.send('我将帮您上传作业至pcrdfans，作业将注明您的昵称及qq。您可以随时发送"算了"或"取消"终止上传。')
        await asyncio.sleep(0.5)
        return
    arg = ss.current_arg_text.strip()
    if arg == '算了' or arg == '取消':
        await ss.finish('已取消上传')

    if ss.current_key.endswith('_team'):
        if len(arg) < 15:
            return
        team, star, equip = arg[:-10], arg[-10:-5], arg[-5:]
        if not re.fullmatch(r'[1-6]{5}', star):
            await ss.pause('请依次输入5个数字表示星级，顺序与队伍相同')
        if not re.fullmatch(r'[01]{5}', equip):
            await ss.pause('请依次输入5个0/1表示专武，顺序与队伍相同')
        star = [int(s) for s in star]
        equip = [int(s) for s in equip]
        team, unknown = chara.roster.parse_team(team)
        if unknown:
            _, name, score = chara.guess_id(unknown)
            await ss.pause(f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}')
        if len(team) != 5:
            await ss.pause('队伍必须由5个角色组成')
        ss.state[ss.current_key] = [chara.fromid(team[i], star[i], equip[i]) for i in range(5)]
    elif ss.current_key == 'confirm':
        if arg == '确认' or arg == '確認':
            ss.state[ss.current_key] = True
    else:
        raise ValueError
    return
