from PIL import Image, ImageDraw, ImageFont
from os import fspath
from typing import Literal, Union
from utils import *
from utils.constant import FONT_PATH, ICON_PATH, AVATAR_PATH, IMG_PATH


FONT_HYWH_22 = ImageFont.truetype(fspath(FONT_PATH.joinpath('汉仪文黑.ttf')), 22)
FONT_HYWH_20 = ImageFont.truetype(fspath(FONT_PATH.joinpath('汉仪文黑.ttf')), 20)
FONT_HYWH_18 = ImageFont.truetype(fspath(FONT_PATH.joinpath('汉仪文黑.ttf')), 18)
FONT_MSYHBD_17 = ImageFont.truetype(fspath(FONT_PATH.joinpath('msyhbd.ttc')), 17)
FONT_MSYH_17 = ImageFont.truetype(fspath(FONT_PATH.joinpath('msyh.ttc')), 17)
FONT_MSYH_12 = ImageFont.truetype(fspath(FONT_PATH.joinpath('msyh.ttc')), 12)

FONT_COLOR = (0, 0, 0, 255) #黑
BACKGROUND_COLOR = (250, 247, 232, 255)
TITLE_BACKCOLOR = (103, 198, 184, 255)
CARD_COLOR = (250, 240, 220, 255)
BORDER_COLOR = (255, 204, 153, 255)
# BORDER_COLOR = (244, 230, 154, 255)

GAP = 20
EDGE = 20
MINIEDGE = 40


class Card:
    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = 750
        self.textfont = FONT_MSYH_17
        self.gap = 5


    @classmethod
    def setDefaultParams(cls, draw, img, Mainuser: mUser=None, headers=None):
        cls.draw: ImageDraw.ImageDraw = draw
        cls.img: Image.Image = img
        if Mainuser != None:
            cls.Mainuser = Mainuser
        if headers != None:
            cls.headers = headers


    # source: 'https://github.com/UNIkeEN/Little-UNIkeEN-Bot/blob/main/utils/responseImage.py'
    def drawRoundedRectangle(self, x1, y1, x2, y2, fill, r = 15, border=False, borderColor=False, borderWidth = 3): 
        self.draw.ellipse((x1, y1, x1+2*r, y1+2*r), fill = fill)
        self.draw.ellipse((x2-2*r, y1, x2, y1+2*r), fill = fill)
        self.draw.ellipse((x1, y2-2*r, x1+2*r, y2), fill = fill)
        self.draw.ellipse((x2-2*r, y2-2*r, x2, y2), fill = fill)
        self.draw.rectangle((x1+r, y1, x2-r, y2), fill = fill)
        self.draw.rectangle((x1, y1+r, x2, y2-r),fill = fill)
        if border:
            self.draw.arc((x1, y1, x1+2*r, y1+2*r), 180, 270, borderColor, borderWidth)
            self.draw.arc((x2-2*r, y1, x2, y1+2*r), 270, 360, borderColor, borderWidth)
            self.draw.arc((x1, y2-2*r, x1+2*r, y2), 90, 180, borderColor, borderWidth)
            self.draw.arc((x2-2*r, y2-2*r, x2, y2), 0, 90, borderColor, borderWidth)
            self.draw.line((x1, y1+r, x1, y2-r), borderColor, borderWidth)
            self.draw.line((x2, y1+r, x2, y2-r), borderColor, borderWidth)
            self.draw.line((x1+r, y1, x2-r, y1), borderColor, borderWidth)
            self.draw.line((x1+r, y2, x2-r, y2), borderColor, borderWidth)
    

    def adjustText(self, x, edge, text: str, font: ImageFont.ImageFont, mode: Literal['m', 'o']) -> Union[tuple[int, str], int]:
        size = font.getbbox(text)[2:]
        edge -= x
        if size[0] > edge:
            norm = font.getbbox('测')[2:]
            newtext = ''
            match mode:
                case 'm':
                    i = 1
                    for char in text:
                        newtext += char
                        if font.getbbox(newtext)[2] + norm[0] > edge*i:
                            newtext += '\n' 
                            i += 1
                case 'o':
                    for char in text:
                        newtext += char
                        if font.getbbox(newtext)[2] + font.getbbox(' ...')[2] > edge:
                            newtext += ' ...'
                            break
            text = newtext
        return text


    def Text(self, x, y, text, font, fill=FONT_COLOR, 
            write=True, omit=False, multiline=False, edge: int=None) -> list[int]:
        if multiline:
            if edge != None:
                text = self.adjustText(x, edge, text, font, mode='m')
            if write:
                self.draw.multiline_text((x, y), text, fill=fill, font=font)
            return self.draw.multiline_textbbox((x, y), text, font=font)
        elif omit:
            text = self.adjustText(x, edge, text, font, mode='o')
            if write:
                self.draw.text((x, y), text, fill=fill, font=font)
            return list(self.draw.textbbox((x, y), text, font=font))
        else:
            if write:
                self.draw.text((x, y), text, fill=fill, font=font)
            return list(self.draw.textbbox((x, y), text, font=font))
    

    def minicard(self, l: list[tuple[gUser, int]], subtitile, loc: tuple, 
                theme: Literal['Like', 'Reply', 'Emoji'], side: Literal['l', 'r', 'c']):
        if side == 'l':
            x1 = MINIEDGE*2
            x2 = int(0.5*self.width-EDGE)
            ch = loc[1] + 30 + len(l)*60 + 20
        elif side == 'r':
            x1 = int(0.5*self.width+EDGE)
            x2 = self.width-MINIEDGE*2
            ch = loc[1] + 30 + len(l)*60 + 20
        elif side == 'c':
            x1 = MINIEDGE*2
            x2 = self.width-MINIEDGE*2
            ch = loc[1] + 30 + 60 + 20
        self.drawRoundedRectangle(
                x1, loc[1]+10, x2, ch, r=10,
                fill=CARD_COLOR, border=True, borderColor=BORDER_COLOR)
        x = x1 + 20
        y = loc[1] + 20
        size = self.Text(x, y, subtitile, font=FONT_HYWH_20)
        x = size[0] + 5
        y = size[3] + 10
        xt = x + 55
        if side == 'l' or side == 'r':
            for item in l:
                user = item[0]
                try:
                    avatar = Image.open(AVATAR_PATH.joinpath('{}.png'.format(user.username))).convert('RGBA').resize((50, 50))
                except:
                    getAvatar(user, self.headers, AVATAR_PATH)
                    avatar = Image.open(AVATAR_PATH.joinpath('{}.png'.format(user.username))).convert('RGBA').resize((50, 50))
                self.img.paste(avatar, (x, y), mask=avatar.split()[3])

                if theme == 'Like':
                    icon = Image.open(ICON_PATH.joinpath('heart.png')).resize((18, 18))
                elif theme == 'Reply':
                    icon = Image.open(ICON_PATH.joinpath('reply.png')).resize((18, 18))
                s = self.Text(xt, y+2, user.username, font=FONT_MSYH_17, omit=True, edge=x2-20)
                self.img.paste(icon, (s[0], s[3]+5), mask=icon.split()[3])
                self.Text(s[0]+20, s[3]+2, str(item[1]), font=FONT_MSYH_17)
                y += 60
        else: 
            width = int((x2 - x1) / 3)
            for i, item in enumerate(l):
                user = item[0]
                try:
                    avatar = Image.open(AVATAR_PATH.joinpath('{}.png'.format(user.username))).convert('RGBA').resize((50, 50))
                except:
                    getAvatar(user, self.headers, AVATAR_PATH)
                    avatar = Image.open(AVATAR_PATH.joinpath('{}.png'.format(user.username))).convert('RGBA').resize((50, 50))
                self.img.paste(avatar, (x, y), mask=avatar.split()[3])
                s = self.Text(xt, y+2, user.username, font=FONT_MSYH_17, omit=True, edge=x+width-20 if i != 2 else x2-20)
                self.Text(xt, s[3]+2, str(item[1]), font=FONT_MSYH_17)
                x += width
                xt += width
            

    

    def calHeight(self, starty) -> int:
        return 0

    def drawCard(self):
        pass