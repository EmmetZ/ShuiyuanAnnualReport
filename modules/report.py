from PIL import Image, ImageDraw, ImageFont
from os import fspath

from utils import MainUser, info
from utils.constant import BASE_FILEPATH
from modules.cards import (
    Postdata,
    Likedata,
    Topicdata,
    WCdata,
    Emojidata,
    Card,
    UserCard,
    LikeCard,
    TopicCard,
    EmojiCard,
    WCcard,
    PostCard,
    GAP,
    EDGE,
)


FONT_PATH = BASE_FILEPATH.joinpath("resources", "Font")
IMG_PATH = BASE_FILEPATH.joinpath("resources", "img")
ICON_PATH = BASE_FILEPATH.joinpath("resources", "icon")

FONT_HYWH_35 = ImageFont.truetype(fspath(FONT_PATH.joinpath("汉仪文黑.ttf")), 35)
FONT_MSYH_17 = ImageFont.truetype(fspath(FONT_PATH.joinpath("msyh.ttc")), 17)

FONT_COLOR = (0, 0, 0, 255)  # 黑
BACKGROUND_COLOR = (250, 247, 232, 255)
TITLE_BACKCOLOR = (103, 198, 184, 255)


class Report:
    def __init__(self, Mainuser: MainUser, year, headers) -> None:
        self.Mainuser = Mainuser
        self.width: int = 750
        self.height: int = 1500

        self.ld = Likedata
        self.pd = Postdata
        self.td = Topicdata
        self.wd = WCdata
        self.ed = Emojidata
        self.textfont = FONT_MSYH_17
        self.headers = headers
        self.cardlist: list[Card] = []
        self.datadict = {}
        self.year = year

    def load_data(self, key: str, vakue: dict):
        self.datadict.update({key: vakue})

    def auto_size(self):
        tmp = 52 + GAP
        for card in self.cardlist:
            tmp = card.cal_height(tmp)
        self.height = tmp

    def generate_title(self):
        logo = Image.open(ICON_PATH.joinpath("shuiyuan.png")).resize((40, 40))
        self.img.paste(logo, (7, 7), mask=logo.split()[3])
        title = f"{self.year}年度报告"
        self.draw.text((55, 5), title, font=FONT_HYWH_35, fill=FONT_COLOR)

    def generate_report(self, savepath):
        self.tmp = Image.new("RGBA", (1, 1), color=BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.tmp)

        self.cardlist.append(UserCard(self.datadict["user"], x1=EDGE, x2=465))
        classdict = {
            "post": PostCard,
            "like": LikeCard,
            "topic": TopicCard,
            "emoji": EmojiCard,
            "wc": WCcard,
        }
        for key in self.datadict:
            if key == "user":
                continue
            self.cardlist.append(
                classdict[key](self.datadict[key], x1=EDGE, x2=self.width - EDGE)
            )
        Card.set_default_params(self.draw, self.tmp, self.Mainuser, self.headers)
        self.auto_size()

        self.img = Image.new("RGBA", (self.width, self.height), color=BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.img)
        self.draw.rectangle((0, 0, self.width, 52), fill=TITLE_BACKCOLOR)
        Card.set_default_params(self.draw, self.img)
        self.generate_title()
        for i, card in enumerate(self.cardlist):
            # process.value = '  正在生成第{}张卡片...'.format(i+1)
            # page.update()
            info("正在生成第{}张卡片...".format(i + 1))
            card.draw_card()
        self.img.save(savepath, "png", dpi=(1200, 1200))
