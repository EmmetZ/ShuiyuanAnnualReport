from .card import (
    GAP,
    FONT_HYWH_22,
    FONT_MSYH_17,
    FONT_MSYH_12,
    FONT_HYWH_18,
    FONT_COLOR,
    CARD_COLOR,
    BORDER_COLOR,
    EDGE,
    AVATAR_PATH,
    get_avatar,
    Card,
)
from PIL import Image


class UserCard(Card):
    def __init__(self, data, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data = data

    def cal_height(self, starty) -> int:
        startx = EDGE + 95
        self.y1 = starty

        size = self.text(
            startx,
            starty + 10,
            text=self.Mainuser.name,
            font=FONT_HYWH_22,
            write=False,
            multiline=True,
            edge=450,
        )
        size = self.text(
            size[0],
            size[3],
            text=self.Mainuser.username,
            font=FONT_MSYH_17,
            write=False,
        )
        if len(self.Mainuser.title) != 0:
            size = self.text(
                size[0],
                size[3],
                text=self.Mainuser.title,
                font=FONT_MSYH_12,
                write=False,
            )
        height = size[3] + 5
        if height < 155:
            height = 155
        self.y2 = height
        return height + GAP

    def draw_card(self):
        self.draw_rounded_rect(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            fill=CARD_COLOR,
            border=False,
            borderColor=BORDER_COLOR,
        )
        try:
            avatar = (
                Image.open(
                    AVATAR_PATH.joinpath("{}.png".format(self.Mainuser.username))
                )
                .convert("RGBA")
                .resize((75, 75))
            )
        except:
            get_avatar(self.Mainuser, self.headers, AVATAR_PATH)
            avatar = (
                Image.open(
                    AVATAR_PATH.joinpath("{}.png".format(self.Mainuser.username))
                )
                .convert("RGBA")
                .resize((75, 75))
            )
        self.img.paste(avatar, (self.x1 + 10, self.y1 + 4), mask=avatar.split()[3])
        if len(self.Mainuser.name) != 0:
            size = self.text(
                self.x1 + 95,
                self.y1 + 10,
                text=self.Mainuser.name,
                font=FONT_HYWH_22,
                multiline=True,
                edge=450,
            )
            size = self.text(
                size[0], size[3], text=self.Mainuser.username, font=FONT_MSYH_17
            )
        else:
            size = self.text(
                self.x1 + 95,
                self.y1 + 20,
                text=self.Mainuser.username,
                font=FONT_HYWH_22,
                multiline=True,
                edge=450,
            )
        if len(self.Mainuser.title) != 0:
            size = self.text(
                size[0], size[3], text=self.Mainuser.title, font=FONT_MSYH_12
            )

        self.draw_rounded_rect(
            self.x2 + 15,
            self.y1,
            self.width - EDGE,
            155,
            fill=CARD_COLOR,
            border=False,
            borderColor=BORDER_COLOR,
        )
        size = self.text(
            self.x2 + 15 + GAP, self.y1 + 10, text="活跃天数：", font=FONT_HYWH_22
        )
        self.draw.text(
            (size[0] + 15, 10 + size[3]),
            "点赞：{:<3d}  发帖：{:<3d}".format(
                self.data["lactday"], self.data["pactday"]
            ),
            font=FONT_HYWH_18,
            fill=FONT_COLOR,
        )
