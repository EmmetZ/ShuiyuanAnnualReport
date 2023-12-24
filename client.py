import json
import qrcode as qrc
from PIL import ImageShow, Image
import re
from pathlib import Path
from collections import Counter
import shutil
from utils import *
from modules.pr import *
from modules import like
from modules import topic
from modules.report import *
from modules.wc import generateWC
from utils.constant import SY_LOGIN_URL, SY_BASE_URL, BASE_FILEPATH, AVATAR_PATH, IMG_PATH, RESULT_DIR, WORD_PATH
from selenium.webdriver.common.by import By

class Client():
    def __init__(self, info) -> None:
        self.driver = None
        self.Mainuser = None
        self.year = None
        self.info = info
            

    def createDataclass(self):
        self.PD = Postdata
        self.LD = Likedata
        self.TD = Topicdata
        self.WD = WCdata
        self.ED = Emojidata


    def getPostData(self):
        self.info('  正在获取发帖信息：', update='nl')
        postlist = getPost(self.Mainuser, self.headers, self.year, self.info)
        self.PD['post'] = len(postlist)
        self.info('  0/4', update='el')
        self.PD['actday'], self.PD['topPostingDay'] = getTopPostingDay(postlist)
        self.info('  1/4')
        self.PD['daylist'] = getDaydist(postlist)
        self.info('  2/4')
        self.PD['monlist'] = getMonthdist(postlist)
        self.info('  3/4')
        postiddict = getIDdict(postlist)
        self.info('  4/4')
        self.PD['topic'] = postiddict
        self.PD['reply_user'], self.ED['retortnum'], self.ED['emojilist'], self.ED['user'] = getDetails(postiddict, self.headers, self.info, self.Mainuser.username)
        self.ED['ncol'] = 6
        del postiddict
        self.PD['reply'], self.PD['replied_user'] = getReply(self.Mainuser, self.headers, self.year, self.info)


    def getLikeData(self):
        self.info('  正在获取点赞信息：', update='nl')
        self.LD['send'], self.LD['actday'], self.LD['like_user'] = like.getLike(self.Mainuser, self.headers, self.year, self.info, filter=1)
        self.LD['receive'], self.LD['liked_user'] = like.getLike(self.Mainuser, self.headers, self.year, self.info, filter=2)

    
    def getTopicData(self):
        self.info('  正在获取话题信息：', update='nl')
        self.TD['num'], self.TD['topic_list'],retortnum, emoji_dict , emoji_user_dict = topic.getTopic(self.Mainuser, self.headers, self.year, self.info)
        self.ED['retortnum'] += retortnum
        self.ED['emojilist'] = sorted(dict(Counter(self.ED['emojilist'])+Counter(emoji_dict)).items(), key=lambda d: d[1], reverse=True)[0:18]
        self.ED['user'] = dict(Counter(self.ED['user'])+Counter(emoji_user_dict))
        


    def getEmojiData(self):
        if self.ED['user'].__contains__(self.Mainuser.username):
            del self.ED['user'][self.Mainuser.username]
        self.ED['user'] = sorted(self.ED['user'].items(), key=lambda d: d[1], reverse=True)[0:3]
        top3 = []
        for i in range(len(self.ED['user'])):
            user = getUser(headers=self.headers, mode='g', username=self.ED['user'][i][0])
            top3.append((user, self.ED['user'][i][1]))
        self.ED['user'] = top3

    
    def getWordCloud(self):
        if self.PD['post'] > 0:
            print('开始生成wordcloud:')
            self.WD['WCpath'] = generateWC()
        else: self.WD['WCpath'] = None


    def loadExtraEmoji(self):
        with BASE_FILEPATH.joinpath('resources', 'extra_emoji.json').open(encoding="utf-8") as f:
            self.ED['extra_emoji'] = json.load(f)


    def getAllData(self):
        self.createDataclass()
        self.getPostData()
        self.getLikeData()
        self.getTopicData()
        self.getEmojiData()
        self.getWordCloud()
        self.loadExtraEmoji()
    

    def loadData(self):
        self.Report = Report(self.Mainuser, self.year, self.headers)
        userdata = {'pactday': self.PD['actday'], 'lactday': self.LD['actday']}
        self.Report.loadData('user', userdata)
        name = ['post', 'like', 'topic', 'emoji', 'wc']
        datalist = [self.PD, self.LD, self.TD, self.ED, self.WD]
        for i in range(5):
            self.Report.loadData(name[i], datalist[i])

    
    def generateReport(self, year):
        if AVATAR_PATH.exists():
            shutil.rmtree(AVATAR_PATH)
        Path(AVATAR_PATH).mkdir()
        if WORD_PATH.exists():
            WORD_PATH.unlink()
        f = WORD_PATH.open('x', encoding='utf-8')
        f.close()
        if IMG_PATH.exists():
            shutil.rmtree(IMG_PATH)
        IMG_PATH.mkdir()
        if not RESULT_DIR.exists():
            RESULT_DIR.mkdir()
        self.year = year
        self.getAllData()
        self.info('  开始生成报告...', update='nl')
        self.loadData()
        result = RESULT_DIR.joinpath(f'{self.Mainuser.username}的{self.year}年度总结.png')
        self.Report.generateReport(result, self.info)
        shutil.rmtree(AVATAR_PATH)
        shutil.rmtree(IMG_PATH)
        self.info('  完成！请在results文件夹中查看')
          

    def login_mannual(self, browser) -> bool:
        self.driver = getWebdriver(browser, headless=False)
        self.driver.get(SY_BASE_URL)
        self.driver.implicitly_wait(10)
        isRedirect(self.driver)
        cookie = self.driver.get_cookie(name='_t')
        # print(cookie)
        self.saveCookie(cookie['name'], cookie['value'])
        return isRedirect(self.driver, refresh=True)
     
        
    def login_cookie(self, browser, cookie) -> bool:
        self.driver = getWebdriver(browser, headless=True)
        cookie_dict = {
            'name': '_t',
            'value': cookie
        }
        self.driver.get(SY_LOGIN_URL)
        self.driver.add_cookie(cookie_dict)
        flag = isRedirect(self.driver, refresh=True)
        if flag:
            self.saveCookie('_t', cookie)
            return True
        else:
            return False
        

    def getmUser(self):
        self.Mainuser = getmUser(self.driver, self.headers)
        return (self.Mainuser.username, self.Mainuser.name)
    
    
    def getQrcode(self, browser):
        self.driver = getWebdriver(browser, headless=True)
        self.driver.get(SY_BASE_URL)
        self.driver.implicitly_wait(10)
        url = self.driver.find_elements(By.XPATH, '/html/body/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/img')[0].get_attribute('src')
        idx = re.findall(r'https://jaccount.sjtu.edu.cn/jaccount/qrcode\?uuid=(\S+)&ts=(\S+)&sig=(\S+)', url)
        url = 'https://jaccount.sjtu.edu.cn/jaccount/confirmscancode?uuid='+idx[0][0]+'&ts='+idx[0][1]+'&sig='+idx[0][2]
        qrcode: Image = qrc.make(url)
        if BASE_FILEPATH.joinpath('resources', 'qrcode.png').exists():
            BASE_FILEPATH.joinpath('resources', 'qrcode.png').unlink()
        qrcode.save(BASE_FILEPATH.joinpath('resources', 'qrcode.png'))   

    
    def saveCookie(self, name: str, value: str):
        self.headers = {
            'Cookie':name + '=' + value,
            'Content-Type': 'application/json',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }