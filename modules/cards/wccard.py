from .card import *

WCdata = {
    'WCpath': None # str
}


class WCcard(Card):
    def __init__(self, data: WCdata, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data: WCdata = data

    
    def calHeight(self, starty) -> int:
        self.y1 = starty
        if self.data['WCpath'] != None:
            size = self.Text(0, self.y1+10, '标题', font=FONT_HYWH_22, write=False)
            self.y2 = size[3] + self.gap + 330 + GAP
        else:
            self.y2 = self.y1

        return self.y2 + GAP
    
    def drawCard(self):
        if self.data['WCpath'] == None:
            return
        if self.data['WCpath'] == None:
            return
        self.drawRoundedRectangle(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1+20
        sy = self.y1+10

        size = self.Text(sx, sy, '年度词云：', font=FONT_HYWH_22)
        wc = Image.open(self.data['WCpath']).resize((660, 330))
        self.img.paste(wc, (size[0]+5, size[3]+self.gap), mask=wc.split()[3])