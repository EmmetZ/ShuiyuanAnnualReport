from .card import (
    Card,
    FONT_HYWH_22,
    FONT_MSYH_17,
    CARD_COLOR,
    GAP,
)
from utils import get_emoji
from PIL import Image
from math import ceil
from utils.constant import IMG_PATH

Emojidata = {
    "retortnum": 0,  # int
    "emojilist": [],  # list
    "user": [],  # list
    "ncol": 0,  # int
    "custom_emoji": {},  # dict
}


class EmojiCard(Card):
    def __init__(self, data, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data = data

    def cal_height(self, starty) -> int:
        self.y1 = starty

        if self.data["retortnum"] > 0:
            size = self.text(0, self.y1 + 10, "标题", font=FONT_HYWH_22, write=False)
            for _ in range(2):
                size = self.text(
                    size[0] + 20,
                    size[3] + self.gap,
                    "测",
                    font=self.textfont,
                    write=False,
                )
            size[3] += self.gap
            for _ in range(ceil(len(self.data["emojilist"]) / self.data["ncol"])):
                size[3] += self.gap + 10 + FONT_MSYH_17.getbbox("233")[3]
            self.y2 = size[3] + self.gap
            if len(self.data["user"]) > 0:
                size[3] += 30 + 1 * 60 + 20
            self.y2 = size[3] + GAP
            return self.y2 + GAP
        else:
            self.y2 = self.y1
            return self.y2

    def draw_card(self):
        if self.data["retortnum"] <= 0:
            return
        self.draw_rounded_rect(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1 + 20
        sy = self.y1 + 10

        size = self.text(sx, sy, "表情：", font=FONT_HYWH_22)
        text = "1. 共被贴表情：{}".format(self.data["retortnum"])
        size = self.text(size[0] + 20, size[3] + self.gap, text, font=self.textfont)
        size = self.text(
            size[0], size[3] + self.gap, "2. 被贴最多的表情", font=self.textfont
        )
        h = size[3] + self.gap
        listlen = len(self.data["emojilist"])
        epoch = ceil(listlen / self.data["ncol"]) * self.data["ncol"]
        for i in range(0, epoch, self.data["ncol"]):
            for j in range(min(listlen - i, self.data["ncol"])):
                w = size[0] + 30 + j * 100
                name = self.data["emojilist"][i + j][0]
                num = self.data["emojilist"][i + j][1]
                try:
                    url = "https://shuiyuan.sjtu.edu.cn/images/emoji/google/{}.png?v=12".format(
                        name
                    )
                    get_emoji(name, url, self.headers, IMG_PATH)
                except Exception as _:
                    if name in self.data["custom_emoji"]:
                        url = self.data["custom_emoji"][name]
                        get_emoji(name, url, self.headers, IMG_PATH)
                    else:
                        s = self.text(
                            w,
                            h + self.gap,
                            "{}: {}".format(name, num),
                            font=FONT_MSYH_17,
                        )
                        continue
                emoji = Image.open(IMG_PATH.joinpath("{}.png".format(name))).convert(
                    "RGBA"
                )
                emoji = emoji.resize((25, 25))
                self.img.paste(emoji, (w, h + self.gap), mask=emoji.split()[3])
                s = self.text(w + 30, h + self.gap, str(num), font=FONT_MSYH_17)
            h = s[3] + 10
        self.minicard(
            self.data["user"], "被谁贴最多表情", (size[0], h + self.gap), "Emoji", "c"
        )
