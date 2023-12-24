from matplotlib import pyplot as plt
from matplotlib import cm
from .card import *


Postdata = {
    'post': None, # int
    'topic': None, # int
    'reply': None, # int
    'actday': None, # int
    'replied_user': None, # list[tuple[gUser, int]]
    'reply_user': None, # list[tuple[gUser, int]]
    'topPostingDay': None, # list
    'daylist': None, # list
    'monlist': None, # list
    # 'category': None # dict
}




class PostCard(Card):
    def __init__(self, data: Postdata, x1=0, y1=0, x2=0, y2=0) -> None:
        super().__init__(x1, y1, x2, y2)
        self.data: Postdata = data
    

    def calHeight(self, starty: int) -> int:
        self.y1 = starty

        size = self.Text(0, self.y1+10, '标题', font=FONT_HYWH_22, write=False)
        for i in range(2):
            size = self.Text(size[0]+20, size[3]+self.gap, '测', font=self.textfont, write=False)
        if self.data['post'] != 0:
            topicnum = len(self.data['topic'])
            if topicnum > 3:
                topicnum = 3
            for _ in range(topicnum + 1):
                size = self.Text(size[0]+20, size[3]+self.gap, '测', font=self.textfont, write=False)
            size = self.Text(size[0], size[3]+self.gap, '测\n测', font=self.textfont, multiline=True)
            for i in range(2):
                size = self.Text(size[0], size[3]+self.gap, '测', font=self.textfont)
                size[3] += 220
        idx = max(len(self.data['replied_user']), len(self.data['reply_user']))
        if idx > 0:
            size[3] += 30 + idx*60 + 20
        self.y2 = size[3] + GAP
        return size[3] + 2*GAP
    

    def drawbar(self, x: list[int], y: list[int], savepath: str, loc: tuple, size: tuple=(700, 250)):
        norm = plt.Normalize(min(y), max(y)) 
        norm_y = norm(y)
        map_vir = cm.get_cmap('autumn_r')
        color = map_vir(norm_y)
        plt.bar(x, y, color=color)
        th = max(y)/100
        for a, b, i in zip(x, y, range(len(x))): 
            if y[i] != 0:
                plt.text(a, b+th, y[i], ha='center', fontsize=10)
        x_major_locator=plt.MultipleLocator(1) 
        ax=plt.gca()
        ax.set_xlim(-0.9+x[0], 0.9+x[-1]) 
        ax.xaxis.set_major_locator(x_major_locator)
        plt.savefig(savepath, transparent=True, dpi=1600)
        plt.clf()
        bar = Image.open(savepath).resize(size)
        self.img.paste(bar, loc, mask=bar.split()[3])


    def drawCard(self):
        self.drawRoundedRectangle(self.x1, self.y1, self.x2, self.y2, fill=CARD_COLOR)
        sx = self.x1+20
        sy = self.y1+10

        size = self.Text(sx, sy, '发帖：', font=FONT_HYWH_22)
        text = '1.共发贴：{}，分布在 {} 个话题中'.format(self.data['post'], len(self.data['topic'])) 
        size = self.Text(size[0]+20, size[3]+self.gap, text, font=self.textfont)
        text = '2.共收到回复：{} 条'.format(str(self.data['reply']))
        size = self.Text(size[0], size[3]+self.gap, text, font=self.textfont, multiline=True)
        if self.data['post'] > 0:
            size = self.Text(size[0], size[3]+self.gap, '3.发帖最多的3个话题:', font=self.textfont)
            tmpx = size[0] + 20 
            tmpx1 = size[0]
            for i, topic in enumerate(self.data['topic']):
                size = self.Text(tmpx, size[3]+self.gap, self.data['topic'][topic]['topic_title'], font=self.textfont, omit=True, edge=650)
                if i == 2:
                    break
            text = '4.发帖最多的日期：'
            for i in range(len(self.data['topPostingDay'])):
                text += '{}  '.format(self.data['topPostingDay'][i][0])
            text += '\n   当天共发帖 {} 条'.format(self.data['topPostingDay'][0][1])
            size = self.Text(tmpx1, size[3]+self.gap, text, font=self.textfont, multiline=True)
            M = max(self.data['daylist'])
            idx = self.data['daylist'].index(M)
            text = '5.一年中，你在 {} 至 {} 时发帖最多，共发 {} 帖'.format(idx, idx+1, M)
            size = self.Text(size[0], size[3]+self.gap, text, font=self.textfont)
            
            savepath = IMG_PATH.joinpath('day.png')
            self.drawbar([i for i in range(24)], self.data['daylist'], savepath, loc=(size[0]-20, size[3]-20))
            size[3] += 220
            M = max(self.data['monlist'])
            idx = self.data['monlist'].index(M)+1
            text = '6.一年中，你在 {} 月发帖最多，共发 {} 帖'.format(idx, M)
            size = self.Text(size[0], size[3]+self.gap, text, font=self.textfont)
            savepath = IMG_PATH.joinpath('month.png')
            self.drawbar([i for i in range(1, 13)], self.data['monlist'], savepath, loc=(size[0]-20, size[3]-20))
            size[3] += 220
            if len(self.data['replied_user']) > 0:
                self.minicard(self.data['replied_user'], '被谁回复最多', (size[0], size[3]+self.gap), 'Reply', 'l')
            if len(self.data['reply_user']) > 0:
                self.minicard(self.data['reply_user'], '最多回复至', (size[0]+int(0.5*self.width), size[3]+self.gap), 'Reply', 'r')