from typing import Literal, Union
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from modules.wc import extract
from utils import *
from urllib.parse import urlencode
from utils.constant import  USER_POST_URL, USER_REPLY_URL, POST_URL
from flet import Page, Text


class Post():
    __timezone = None

    @classmethod
    def setTimezone(cls, timezone):
        cls.__timezone = timezone
   

    def __init__(
        self,
            topic_id: int,
            post_id: int,
            category_id: int,
            time: str,
            topic_title: str
            ) -> None:
        self.topic_id = topic_id
        self.post_id = post_id
        self.category_id = category_id
        self.time = time
        self.topic_title = topic_title  


    def getTime(self, unit: Literal['year', 'mon', 'day', 'hour']) -> int:
        timezone = ZoneInfo(self.__timezone)
        ddt = datetime.strptime(self.time,'%Y-%m-%dT%H:%M:%S.%fZ')
        dt = ddt.astimezone(timezone)
        match unit:
            case 'year':
                return dt.year
            case 'mon':
                return dt.month
            case 'day':
                return dt.day
            case 'hour':
                return dt.hour  
    
    

def getPost(MainUser: mUser, driver: Union[webdriver.Edge, webdriver.Chrome], year, info) -> list:
    Post.setTimezone(MainUser.timezone)
    flag = 0
    offset = 0
    count = 0
    post_list = []
    info(update='el')

    baseurl = USER_POST_URL.format(MainUser.username)

    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, driver)
        user_actions = req['user_actions']
        for act in user_actions:
            if isInSelectYear(act['created_at'], MainUser.timezone, year):
                flag = 1
                break
            offset += 1
        if flag: break

    flag = 0
    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, driver)
        user_actions = req['user_actions']
        if len(user_actions) < 1000:
            flag = 1
        for act in user_actions:
            if not isInSelectYear(act['created_at'], MainUser.timezone, year):
                flag = 1
                break

            count += 1
            offset += 1
            if count % 1000 == 0:
                info('已统计{}'.format(count))
            post = Post(
                topic_id = act['topic_id'],
                post_id = act['post_id'],
                category_id = act['category_id'],
                time = act['created_at'],
                topic_title = act['title'])
            post_list.append(post) 

        if flag: break
    info(' 已统计{}'.format(count))
    return post_list




def getReply(MainUser: mUser, driver: Union[webdriver.Edge, webdriver.Chrome], year, info) -> tuple[int, list]:
    flag = 0
    offset = 0
    count = 0
    reply_user_list = {}
    baseurl = USER_REPLY_URL.format(MainUser.username)
    info(update='nl')

    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, driver)
        user_actions = req['user_actions']
        for act in user_actions:
            if isInSelectYear(act['created_at'], MainUser.timezone, year):
                flag = 1
                break
            offset += 1
        if flag: break

    flag = 0
    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, driver)
        user_actions = req['user_actions']
        if len(user_actions) < 1000:
            flag = 1
        for act in user_actions:
            if not isInSelectYear(act['created_at'], MainUser.timezone, year):
                flag = 1
                break

            count += 1
            offset += 1
            if count % 1000 == 0:
                info('  {}'.format(count))  
            if act['username'] not in reply_user_list:
                reply_user_list.update({act['username']: 0})
            reply_user_list[act['username']] += 1
        if flag: break

    reply_user_list = sorted(reply_user_list.items(), key=lambda d: d[1], reverse=True)[0:3]
    top3 = list()
    for i in range(len(reply_user_list)):
        user = getUser(driver=driver, mode='g', username=reply_user_list[i][0])
        top3.append((user, reply_user_list[i][1]))
    info('  {}'.format(count))
    return count, top3


def getTopPostingDay(post_list: list[Post]) -> tuple[int, list]:
    daydict = {}

    for i, post in enumerate(post_list):
        day = '{}.{}'.format(post.getTime('mon'), post.getTime('day'))
        if day not in daydict:
            daydict.update({day: 0})
        daydict[day] += 1
    
    daydict = sorted(daydict.items(), key=lambda d: d[1], reverse=True)
    Topday = []
    Max = daydict[0][1]
    for item in daydict:
        if item[1] == Max:
            Topday.append(item)
        else: break
    return len(daydict), Topday


def getDaydist(post_list: list[Post]) -> list:
    period = [0 for i in range(24)]
    for i, post in enumerate(post_list):
        period[post.getTime('hour')] += 1
    return period


def getMonthdist(post_list: list[Post]) -> list:
    mon = [0 for i in range(12)]
    for i, post in enumerate(post_list):
        mon[post.getTime('mon')-1] += 1
    return mon


def getIDdict(post_list: list[Post]) -> dict:
    x = {}
    for i, item in enumerate(post_list):
        if item.topic_id not in x:
            x.update({item.topic_id: {
                'topic_title': item.topic_title,
                'posts_id': []
            }})
        x[item.topic_id]['posts_id'].append(item.post_id)
    x = dict(sorted(x.items(), key=lambda d: len(d[1]['posts_id']), reverse=True))
    return x     


def getDetails(x: dict[list], driver: Union[webdriver.Edge, webdriver.Chrome], info) -> tuple[list, int, dict]:
    '''
    x = {
        topic_id: {
            'topic_title': str,
            'posts_id': list
    }
    '''
    reply_user_dict = {}
    info(update='nl')

    M = 200
    topicnum = len(x)
    i = 0
    retortnum = 0
    emojidict = {}
    for item in x:
        baseurl = POST_URL.format(str(item))
        num = len(x[item]['posts_id'])
        flag = 1
        start = 0
        end = M
        while flag:
            url = baseurl
            if end > num:
                ids = x[item]['posts_id'][start:end]
                flag = 0
            else:
                ids = x[item]['posts_id'][start:end]
            for j, id in enumerate(ids):
                if j > 0:
                    url += '&'
                url += urlencode({'post_ids[]': id}) 

            req = request(url, driver)
            posts = req['post_stream']['posts']
            for post in posts:
                extract(post['cooked'])
                if post.__contains__('reply_to_user'):
                    pr = post['reply_to_user']
                    if pr['username'] not in reply_user_dict:
                        reply_user_dict.update({pr['username']: 0})
                    reply_user_dict[pr['username']] += 1
                # 计算贴表情
                if len(post['retorts']) > 0:
                    for retort in post['retorts']:
                        retortnum += len(retort)
                        if retort['emoji'] not in emojidict:
                            emojidict.update({retort['emoji']: 0})
                        emojidict[retort['emoji']] += len(retort['usernames'])
        i += 1
        if i % 5 == 0:
            info('  {}/{}'.format(i, topicnum))
    info('  {}/{}'.format(i, topicnum))
    reply_user_dict = sorted(reply_user_dict.items(), key=lambda d: d[1], reverse=True)[0:3]
    top3 = list()
    for i in range(len(reply_user_dict)):
        user = getUser(driver=driver, mode='g', username=reply_user_dict[i][0])
        top3.append((user, reply_user_dict[i][1]))
    
    return top3, retortnum, emojidict



'''
def getDetails_mp(x: dict[list], type: Literal['edge', 'chrome'], service_path, cookie: dict, conc: Connection, show=True):
    if type == 'edge':
        driver = getWebdriver(Browser.EDGE, headless=True)
    if type == 'chrome':
        driver = getWebdriver(Browser.CHROME, headless=True)
    driver.get(SY_LOGIN_URL)
    driver.add_cookie(cookie)
    isRedirect(driver, refresh=True)
    reply_user_dict = {}

    M = 200
    topicnum = len(x)
    retortnum = 0
    emojidict = {}
    i = 0
    for item in x:
        baseurl = POST_URL.format(str(item))
        num = len(x[item])
        flag = 1
        start = 0
        end = M
        while flag:
            url = baseurl
            if end > num:
                ids = x[item][start:end]
                flag = 0
            else:
                ids = x[item][start:end]
            for id in ids:
                url = url + 'post_ids[]={}&'.format(id)
            req = request(url, driver)
            posts = req['post_stream']['posts']
            for post in posts:
                extract(post['cooked'])
                try:
                    pr = post['reply_to_user']
                    if pr['username'] not in reply_user_dict:
                        reply_user_dict.update({pr['username']: 0})
                    reply_user_dict[pr['username']] += 1
                except: continue

                if len(post['retorts']) > 0:
                    for retorts in post['retorts']:
                        for retort in retorts:
                            retortnum += len(retort)
                            if retort['emoji'] not in emojidict:
                                emojidict.update({retort['emoji']: 0})
                                emojidict[retort['emoji']] += len(retort['usernames'])
        i += 1
        if show:
            print('\r{}/{}'.format(i, topicnum), flush=True, end='')
    # reply_user_dict = sorted(reply_user_dict.items(), key=lambda d: d[1], reverse=True)[0:3]
    driver.quit()
    print(' ')
    try:
        conc.send(reply_user_dict)
    except ValueError as e:
        print(e)
        print('发送对象过大')
        os.system('pause')
        exit(1)


def getDetails_multiprocess(x: dict, num: int, driver: Union[Edge, Chrome], service_path, cookie: dict):
    subdict = split_dict(x, num)
    if type(driver) == Edge:
        t = 'edge'
        service_path = service_path[0]
    else: 
        t = 'chrome'
        service_path = service_path[1]
    p = [0 for i in range(2*num)]
    process = [0 for i in range(num)]
    for i in range(num):
        p[2*i], p[2*i+1] = Pipe()
        process[i] = Process(target=getDetails_mp, args=(subdict[i], t, service_path, cookie, p[2*i], i==0,))
        process[i].start()
    r = []
    for i in range(num):
        r.append(p[2*i+1].recv())
    for i in range(num):
        process[i].join()
    result = Counter({})
    for i in range(num):
        result += Counter(r[i])
    result = dict(result)
    result = sorted(result.items(), key=lambda d: d[1], reverse=True)[0:3]
    top3 = list()
    for i in range(3):
        user = getUser(driver=driver, mode='g', username=result[i][0])
        top3.append((user, result[i][1]))
    return top3
'''








