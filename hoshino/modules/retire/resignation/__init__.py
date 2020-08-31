from io import BytesIO
import os
import requests
import aiohttp
from PIL import Image
from hoshino import Service
from hoshino import Service, priv as Priv
from hoshino.util import FreqLimiter
import matplotlib.pyplot as plt
from .data_source import add_text,get_apikey,add_text1
import base64
background1 = '公会离职报告模板.jpg'
background2 = '公会本期报告模板.jpg'
_time_limit = 60*60#频率限制
_lmt = FreqLimiter(_time_limit)
yobot_url = 'https://yobot.maxesisn.online' #请修改为你的yobot网址 例：http://xxx.xx.xxx.xxx:xxxx
sv = Service('离职报告')
@sv.on_keyword(keywords='生成离职报告')
async def create_resignation_report(bot, event):
    uid = event['user_id']
    #nickname = event['sender']['nickname']
    gid = event['group_id']
    apikey = get_apikey(gid)
    url = f'{yobot_url}/clan/{gid}/statistics/api/?apikey={apikey}'
    if not _lmt.check(uid):
        await bot.send(event, f'{_time_limit/3600}小时仅能生成一次报告', at_sender=True)
        return
    _lmt.start_cd(uid)
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        damage_to_boss[chl['boss_num']-1] += chl['damage']
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['damage'] != 0:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    plt.figure(figsize=(3.5, 3.5))
    labels = [f'{x+1}王' for x in range(0,5) if times_to_boss[x] != 0]
    sizes = [x for x in times_to_boss if x != 0]
    patches, l_text, p_text = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,labeldistance=1.1)
    for t in l_text:
        #为标签设置字体大小
        t.set_size(15)
    for t in p_text:
        #为比例设置字体大小
        t.set_size(10)
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    pie_img = Image.open(buf)

    #清空饼图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = damage_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制柱状图
    recs = ax.bar(x,y,width=0.618)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(damage_to_boss[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background1))
    img.paste(pie_img, (635,910), mask=pie_img.split()[3])
    img.paste(bar_img, (130,950), mask=bar_img.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    year = '2020'
    month = '8'
    constellation = '狮子'
    
    add_text(img, row1, position=(400,630), textsize=35)
    add_text(img, row2, position=(853,630), textsize=35)
    add_text(img, year, position=(355,443), textsize=40)
    add_text(img, month, position=(565,443), textsize=40)
    add_text(img, constellation, position=(710,443), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 515), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(270,361), textsize=39)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')

@sv.on_keyword(keywords='生成会战报告')
async def create_resignation_report(bot, event):
    uid = event['user_id']
    #nickname = event['sender']['nickname']
    gid = event['group_id']
    apikey = get_apikey(gid)
    url = f'{yobot_url}/clan/{gid}/statistics/api/?apikey={apikey}'
    if not _lmt.check(uid):
        await bot.send(event, f'{_time_limit/3600}小时仅能生成一次报告', at_sender=True)
        return
    _lmt.start_cd(uid)
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        damage_to_boss[chl['boss_num']-1] += chl['damage']
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['damage'] != 0:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    plt.figure(figsize=(3.5, 3.5))
    labels = [f'{x+1}王' for x in range(0,5) if times_to_boss[x] != 0]
    sizes = [x for x in times_to_boss if x != 0]
    patches, l_text, p_text = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,labeldistance=1.1)
    for t in l_text:
        #为标签设置字体大小
        t.set_size(15)
    for t in p_text:
        #为比例设置字体大小
        t.set_size(10)
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    pie_img = Image.open(buf)

    #清空饼图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = damage_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制柱状图
    recs = ax.bar(x,y,width=0.618)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(damage_to_boss[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background2))
    img.paste(pie_img, (635,910), mask=pie_img.split()[3])
    img.paste(bar_img, (130,950), mask=bar_img.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    year = '2020'
    month = '8'
    constellation = '狮子'
    
    add_text(img, row1, position=(400,630), textsize=35)
    add_text(img, row2, position=(853,630), textsize=35)
    add_text(img, year, position=(355,443), textsize=40)
    add_text(img, month, position=(565,443), textsize=40)
    add_text(img, constellation, position=(710,443), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 515), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(270,361), textsize=39)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')


@sv.on_rex(r'^看看报告$')#, normalize=False)
async def create_resignation_report(bot, ctx):#, match):
    if not Priv.check_priv(ctx,Priv.ADMIN):
        return
    for m in ctx['message']:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
    gid = ctx['group_id']
    apikey = get_apikey(gid)
    url = f'{yobot_url}/clan/{gid}/statistics/api/?apikey={apikey}'
    _lmt.start_cd(uid)
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        damage_to_boss[chl['boss_num']-1] += chl['damage']
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['damage'] != 0:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    plt.figure(figsize=(3.5, 3.5))
    labels = [f'{x+1}王' for x in range(0,5) if times_to_boss[x] != 0]
    sizes = [x for x in times_to_boss if x != 0]
    patches, l_text, p_text = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,labeldistance=1.1)
    for t in l_text:
        #为标签设置字体大小
        t.set_size(15)
    for t in p_text:
        #为比例设置字体大小
        t.set_size(10)
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    pie_img = Image.open(buf)

    #清空饼图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = damage_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制柱状图
    recs = ax.bar(x,y,width=0.618)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(damage_to_boss[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background2))
    img.paste(pie_img, (635,910), mask=pie_img.split()[3])
    img.paste(bar_img, (130,950), mask=bar_img.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    year = '2020'
    month = '8'
    constellation = '狮子'
    
    add_text(img, row1, position=(400,630), textsize=35)
    add_text(img, row2, position=(853,630), textsize=35)
    add_text(img, year, position=(355,443), textsize=40)
    add_text(img, month, position=(565,443), textsize=40)
    add_text(img, constellation, position=(710,443), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 515), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(270,361), textsize=39)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ctx, f'[CQ:image,file={base64_str}]')
