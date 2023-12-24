from .card import Card, FONT_HYWH_22, ICON_PATH, GAP, CARD_COLOR, Image, FONT_MSYHBD_17

Topicdata = {
    'num': None, # int
    'topic_list': None # list[tuple[str, int]]
}


class TopicCard(Card):
    def __init__(self, data: Topicdata, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data: Topicdata = data


    def calHeight(self, starty) -> int:
        self.y1 = starty

        if self.data['num'] > 0:
            size = self.Text(0, self.y1+10, '标题', font=FONT_HYWH_22, write=False)
            for _ in range(2+len(self.data['topic_list'])):
                size = self.Text(size[0]+20, size[3]+self.gap, '测', font=self.textfont, write=False)
            self.y2 = size[3] + GAP
            return size[3] + 2*GAP
        else:
            self.y2 = self.y1
            return self.y2


    def drawCard(self):
        if self.data['num'] <= 0:
            return
        icon = Image.open(ICON_PATH.joinpath('heart.png')).resize((18, 18))
        self.drawRoundedRectangle(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1+20
        sy = self.y1+10

        size = self.Text(sx, sy, '话题：', font=FONT_HYWH_22)
        text = f"1.共创建话题：{self.data['num']}"
        size = self.Text(size[0]+20, size[3]+self.gap, text, font=self.textfont)
        text = '2.最受欢迎的话题：'
        size = self.Text(size[0], size[3]+self.gap, text, font=self.textfont)
        tmpx = size[0]+20
        for topic in self.data['topic_list']:
            tmpy = size[3]+self.gap
            size = self.Text(tmpx, size[3]+self.gap, topic[0], font=FONT_MSYHBD_17, omit=True, edge=600)
            s = self.Text(size[2]+15, tmpy, str(topic[1]), font=FONT_MSYHBD_17)
            self.img.paste(icon, (s[2]+3, s[1]-2), mask=icon.split()[3])
