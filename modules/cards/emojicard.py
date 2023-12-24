from .card import *
from math import ceil

Emojidata = {
    'retortnum': None, # int
    'emojilist': None, # list
    'ncol': None, # int
    'extra_emoji': None # dict
}


class EmojiCard(Card):
    def __init__(self, data: Emojidata, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data: Emojidata = data
    

    def calHeight(self, starty) -> int:
        self.y1 = starty

        if self.data['retortnum'] > 0:
            size = self.Text(0, self.y1+10, '标题', font=FONT_HYWH_22, write=False)
            for i in range(2):
                size = self.Text(size[0]+20, size[3]+self.gap, '测', font=self.textfont, write=False)
            size [3] += self.gap
            for i in range(ceil(len(self.data['emojilist'])/self.data['ncol'])):
                size[3] += self.gap + 10 + FONT_MSYH_17.getbbox('233')[3]
            self.y2 = size[3] + self.gap
            return self.y2 + GAP
        else:
            self.y2 = self.y1
            return self.y2
    
    def drawCard(self):
        if self.data['retortnum'] <= 0:
            return
        self.drawRoundedRectangle(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1+20
        sy = self.y1+10

        size = self.Text(sx, sy, '贴表情数据：', font=FONT_HYWH_22)
        text = '1.共被贴表情：{}'.format(self.data['retortnum'])
        size = self.Text(size[0]+20, size[3]+self.gap, text, font=self.textfont)
        size = self.Text(size[0], size[3]+self.gap, '2.被贴最多的表情', font=self.textfont)
        h = size[3] + self.gap
        listlen = len(self.data['emojilist'])
        epoch = ceil(listlen/self.data['ncol']) * self.data['ncol']
        for i in range(0, epoch, self.data['ncol']):
            for j in range(min(listlen-i, self.data['ncol'])):
                w = size[0] + 30 + j*100
                name = self.data['emojilist'][i+j][0]
                num = self.data['emojilist'][i+j][1]
                try:
                    url = 'https://shuiyuan.sjtu.edu.cn/images/emoji/google/{}.png?v=12'.format(name)
                    getEmoji(name, url, self.headers, IMG_PATH)
                except Exception as e:
                    if name in self.data['extra_emoji']:
                        url = self.data['extra_emoji'][name]
                        getEmoji(name, url, self.headers, IMG_PATH)
                    else:
                        s = self.Text(w, h+self.gap, '{}: {}'.format(name, num), font=FONT_MSYH_17)
                        continue
                emoji = Image.open(IMG_PATH.joinpath('{}.png'.format(name))).convert('RGBA')
                emoji = emoji.resize((25, 25)) 
                self.img.paste(emoji, (w, h+self.gap), mask=emoji.split()[3])
                s = self.Text(w+30, h+self.gap, str(num), font=FONT_MSYH_17)
            h = s[3] + 10