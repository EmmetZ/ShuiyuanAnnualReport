from PIL import Image, ImageDraw, ImageFont
from os import fspath
from typing import Literal, Union
from utils import MainUser, User, get_avatar
from utils.constant import FONT_PATH, ICON_PATH, AVATAR_PATH


FONT_HYWH_22 = ImageFont.truetype(fspath(FONT_PATH.joinpath("汉仪文黑.ttf")), 22)
FONT_HYWH_20 = ImageFont.truetype(fspath(FONT_PATH.joinpath("汉仪文黑.ttf")), 20)
FONT_HYWH_18 = ImageFont.truetype(fspath(FONT_PATH.joinpath("汉仪文黑.ttf")), 18)
FONT_MSYHBD_17 = ImageFont.truetype(fspath(FONT_PATH.joinpath("msyhbd.ttc")), 17)
FONT_MSYH_17 = ImageFont.truetype(fspath(FONT_PATH.joinpath("msyh.ttc")), 17)
FONT_MSYH_12 = ImageFont.truetype(fspath(FONT_PATH.joinpath("msyh.ttc")), 12)

FONT_COLOR = (0, 0, 0, 255)  # 黑
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
    def set_default_params(cls, draw, img, Mainuser: MainUser = None, headers=None):
        cls.draw: ImageDraw.ImageDraw = draw
        cls.img: Image.Image = img
        if Mainuser is not None:
            cls.Mainuser = Mainuser
        if headers is not None:
            cls.headers = headers

    # source: 'https://github.com/UNIkeEN/Little-UNIkeEN-Bot/blob/main/utils/responseImage.py'
    def draw_rounded_rect(
        self, x1, y1, x2, y2, fill, r=15, border=False, borderColor=False, borderWidth=3
    ):
        self.draw.ellipse((x1, y1, x1 + 2 * r, y1 + 2 * r), fill=fill)
        self.draw.ellipse((x2 - 2 * r, y1, x2, y1 + 2 * r), fill=fill)
        self.draw.ellipse((x1, y2 - 2 * r, x1 + 2 * r, y2), fill=fill)
        self.draw.ellipse((x2 - 2 * r, y2 - 2 * r, x2, y2), fill=fill)
        self.draw.rectangle((x1 + r, y1, x2 - r, y2), fill=fill)
        self.draw.rectangle((x1, y1 + r, x2, y2 - r), fill=fill)
        if border:
            self.draw.arc(
                (x1, y1, x1 + 2 * r, y1 + 2 * r), 180, 270, borderColor, borderWidth
            )
            self.draw.arc(
                (x2 - 2 * r, y1, x2, y1 + 2 * r), 270, 360, borderColor, borderWidth
            )
            self.draw.arc(
                (x1, y2 - 2 * r, x1 + 2 * r, y2), 90, 180, borderColor, borderWidth
            )
            self.draw.arc(
                (x2 - 2 * r, y2 - 2 * r, x2, y2), 0, 90, borderColor, borderWidth
            )
            self.draw.line((x1, y1 + r, x1, y2 - r), borderColor, borderWidth)
            self.draw.line((x2, y1 + r, x2, y2 - r), borderColor, borderWidth)
            self.draw.line((x1 + r, y1, x2 - r, y1), borderColor, borderWidth)
            self.draw.line((x1 + r, y2, x2 - r, y2), borderColor, borderWidth)

    def adjust_text(
        self, x, edge, text: str, font: ImageFont.ImageFont, mode: Literal["m", "o"]
    ) -> Union[tuple[int, str], int]:
        size = font.getbbox(text)[2:]
        edge -= x
        if size[0] > edge:
            norm = font.getbbox("测")[2:]
            newtext = ""
            match mode:
                case "m":
                    i = 1
                    for char in text:
                        newtext += char
                        if font.getbbox(newtext)[2] + norm[0] > edge * i:
                            newtext += "\n"
                            i += 1
                case "o":
                    for char in text:
                        newtext += char
                        if font.getbbox(newtext)[2] + font.getbbox(" ...")[2] > edge:
                            newtext += " ..."
                            break
            text = newtext
        return text

    def text(
        self,
        x,
        y,
        text,
        font,
        fill=FONT_COLOR,
        write=True,
        omit=False,
        multiline=False,
        edge: int = None,
    ) -> list[int]:
        if multiline:
            if edge is not None:
                text = self.adjust_text(x, edge, text, font, mode="m")
            if write:
                self.draw.multiline_text((x, y), text, fill=fill, font=font)
            return self.draw.multiline_textbbox((x, y), text, font=font)
        elif omit:
            text = self.adjust_text(x, edge, text, font, mode="o")
            if write:
                self.draw.text((x, y), text, fill=fill, font=font)
            return list(self.draw.textbbox((x, y), text, font=font))
        else:
            if write:
                self.draw.text((x, y), text, fill=fill, font=font)
            return list(self.draw.textbbox((x, y), text, font=font))

    def minicard(
        self,
        user_list: list[tuple[User, int]],
        subtitile,
        loc: tuple,
        theme: Literal["Like", "Reply", "Emoji"],
        side: Literal["l", "r", "c"],
    ):
        if side == "l":
            x1 = MINIEDGE * 2
            x2 = int(0.5 * self.width - EDGE)
            ch = loc[1] + 30 + len(user_list) * 60 + 20
        elif side == "r":
            x1 = int(0.5 * self.width + EDGE)
            x2 = self.width - MINIEDGE * 2
            ch = loc[1] + 30 + len(user_list) * 60 + 20
        elif side == "c":
            x1 = MINIEDGE * 2
            x2 = self.width - MINIEDGE * 2
            ch = loc[1] + 30 + 60 + 20
        self.draw_rounded_rect(
            x1,
            loc[1] + 10,
            x2,
            ch,
            r=10,
            fill=CARD_COLOR,
            border=True,
            borderColor=BORDER_COLOR,
        )
        x = x1 + 20
        y = loc[1] + 20
        size = self.text(x, y, subtitile, font=FONT_HYWH_20)
        x = size[0] + 5
        y = size[3] + 10
        xt = x + 55
        if side == "l" or side == "r":
            for item in user_list:
                user = item[0]
                try:
                    avatar = (
                        Image.open(AVATAR_PATH.joinpath("{}.png".format(user.username)))
                        .convert("RGBA")
                        .resize((50, 50))
                    )
                except:
                    get_avatar(user, self.headers, AVATAR_PATH)
                    avatar = (
                        Image.open(AVATAR_PATH.joinpath("{}.png".format(user.username)))
                        .convert("RGBA")
                        .resize((50, 50))
                    )
                self.img.paste(avatar, (x, y), mask=avatar.split()[3])

                if theme == "Like":
                    icon = Image.open(ICON_PATH.joinpath("heart.png")).resize((18, 18))
                elif theme == "Reply":
                    icon = Image.open(ICON_PATH.joinpath("reply.png")).resize((18, 18))
                s = self.text(
                    xt, y + 2, user.username, font=FONT_MSYH_17, omit=True, edge=x2 - 20
                )
                self.img.paste(icon, (s[0], s[3] + 5), mask=icon.split()[3])
                self.text(s[0] + 20, s[3] + 2, str(item[1]), font=FONT_MSYH_17)
                y += 60
        else:
            width = int((x2 - x1) / 3)
            for i, item in enumerate(user_list):
                user = item[0]
                try:
                    avatar = (
                        Image.open(AVATAR_PATH.joinpath("{}.png".format(user.username)))
                        .convert("RGBA")
                        .resize((50, 50))
                    )
                except:
                    get_avatar(user, self.headers, AVATAR_PATH)
                    avatar = (
                        Image.open(AVATAR_PATH.joinpath("{}.png".format(user.username)))
                        .convert("RGBA")
                        .resize((50, 50))
                    )
                self.img.paste(avatar, (x, y), mask=avatar.split()[3])
                s = self.text(
                    xt,
                    y + 2,
                    user.username,
                    font=FONT_MSYH_17,
                    omit=True,
                    edge=x + width - 20 if i != 2 else x2 - 20,
                )
                self.text(xt, s[3] + 2, str(item[1]), font=FONT_MSYH_17)
                x += width
                xt += width

    def cal_height(self, starty) -> int:
        NotImplementedError

    def draw_card(self):
        NotImplementedError
