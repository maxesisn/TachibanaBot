from configparser import NoOptionError
import os
import configparser
from hoshino import Service, util

sv = Service('assshole_executor')

EXEC_PATH = os.path.expanduser('~/.hoshino/exec.ini')
exec_config = configparser.ConfigParser()
exec_config.read(EXEC_PATH, encoding="utf-8")


@sv.on_prefix('击毙海豹')
async def executor(bot, ev):
    uid = [ev.user_id]
    asshole_id = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            asshole_id = int(m.data['qq'])
    if asshole_id == 0:
        return
    asshole_id = str(asshole_id)
    sections = exec_config.sections()
    if asshole_id not in sections:
        exec_config.add_section(asshole_id)

    try:
        exec_config.get(asshole_id, "user_id")
        if uid not in exec_config.get(asshole_id, "user_id"):
            uid.append(exec_config.get(asshole_id, "user_id"))
        else:
            await bot.send(ev, "您已经投票击毙过该海豹了！")
            return
    except NoOptionError as e:
        exec_config.set(asshole_id, "user_id", uid)
        await bot.send(ev, f"恭喜{uid}成功投票击毙{asshole_id}!")
        exec_config.write(open(EXEC_PATH, "a"))
    else:
        exec_config.set(asshole_id, "user_id", uid)
        await bot.send(ev, f"恭喜{uid}成功投票击毙{asshole_id}!")
        exec_config.write(open(EXEC_PATH, "a"))

    if len(uid) > 30:
        exec_config.remove_section(asshole_id)
        ev.user_id = asshole_id
        await util.silence(ev, 30*60)
        return
