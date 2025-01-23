from .card import (
    Card,
    FONT_HYWH_22,
    CARD_COLOR,
    GAP,
)
from PIL import Image
from utils.constant import ICON_PATH


Likedata = {
    "send": 0,  # int
    "receive": 0,  # int
    "actday": 0,  # int
    "like_user": [],  # list[tuple[gUser, int]]
    "liked_user": [],  # list[tuple[gUser, int]]
}


class LikeCard(Card):
    def __init__(self, data, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data = data

    def cal_height(self, starty) -> int:
        self.y1 = starty

        size = self.text(0, self.y1 + 10, "标题", font=FONT_HYWH_22, write=False)
        for _ in range(2):
            size = self.text(
                size[0] + 20, size[3] + self.gap, "测", font=self.textfont, write=False
            )
        idx = max(len(self.data["like_user"]), len(self.data["liked_user"]))
        if idx > 0:
            size[3] += 30 + idx * 60 + 20
        self.y2 = size[3] + GAP
        return size[3] + 2 * GAP

    def draw_card(self):
        self.draw_rounded_rect(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1 + 20
        sy = self.y1 + 10

        icon = Image.open(ICON_PATH.joinpath("heart.png")).resize((18, 18))
        size = self.text(sx, sy, "点赞：", font=FONT_HYWH_22)
        text = "1. 送出赞：{}".format(str(self.data["send"]))
        size = self.text(size[0] + 20, size[3] + self.gap, text, font=self.textfont)
        self.img.paste(icon, (size[2] + 3, size[1] - 1), mask=icon.split()[3])
        text = "2. 收到赞：{}".format(str(self.data["receive"]))
        size = self.text(size[0], size[3] + self.gap, text, font=self.textfont)
        self.img.paste(icon, (size[2] + 3, size[1] - 1), mask=icon.split()[3])
        if len(self.data["like_user"]) > 0:
            self.minicard(
                self.data["like_user"],
                "赞最多",
                (size[0], size[3] + self.gap),
                "Like",
                "l",
            )
        if len(self.data["liked_user"]) > 0:
            self.minicard(
                self.data["liked_user"],
                "被谁赞得最多",
                (size[0], size[3] + self.gap),
                "Like",
                "r",
            )
