import sqlite3
from PIL import Image,ImageFont,ImageDraw
from os import path

font_path = path.join(path.dirname(__file__), 'TXQYW3.ttf')

def add_text(img: Image,text:str,textsize:int,font=font_path,textfill='black',position:tuple=(0,0)):
    #textsize 文字大小
    #font 字体，默认微软雅黑
    #textfill 文字颜色，默认黑色
    #position 文字偏移（0,0）位置，图片左上角为起点
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img

def add_text1(img: Image,text:str,textsize:int,font=font_path,textfill='white',position:tuple=(0,0)):
    #textsize 文字大小
    #font 字体，默认微软雅黑
    #textfill 文字颜色，默认黑色
    #position 文字偏移（0,0）位置，图片左上角为起点
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img
    
def get_apikey(gid: int) -> str:

    #请指定下一行代码中yobot的数据库路径
    #例：db_path = 'C:/Users/Administrator/Desktop/yobot/yobot/src/client/yobot_data/yobotdata.db'
    db_path = '/root/Bot/Bot_1/TachibanaBot_1/hoshino/modules/yobot/yobot/src/client/yobot_data/yobotdata.db'

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'select apikey from clan_group where group_id={gid}')
    apikey = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return apikey 