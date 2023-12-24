from utils import *
from modules.wc import extract
from utils.constant import  USER_TOPIC_URL, TOPIC_URL
from selenium import webdriver
from flet import Text, Page



def getTopic(MainUser: mUser, driver: webdriver.Edge, year, info) -> tuple[int, list, int, dict]:
    flag = 0
    offset = 0
    count = 0
    topic_id_list = list()
    info(update='nl')

    baseurl = USER_TOPIC_URL.format(MainUser.username)
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
    
    if flag == 0: 
        return 0
    
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
            if count % 500 == 0:
                info(f'  {count}')
            topic_id_list.append(act['topic_id'])
        if flag: break
    
    info(f'  {count}')
    topic_list = dict()
    retortnum = 0
    emojidict = {}
    for i, id in enumerate(topic_id_list):
        topic_url = TOPIC_URL.format(id)
        req = request(topic_url, driver)
        try:
            if req['post_stream']['posts'][0]['cooked_hidden'] == 'true':
                pass
        except:
            extract(req['post_stream']['posts'][0]['cooked'])
        if len(req['post_stream']['posts'][0]['retorts']) > 0:
            for retort in req['post_stream']['posts'][0]['retorts']:
                retortnum += len(retort)
                if retort['emoji'] not in emojidict:
                    emojidict.update({retort['emoji']: 0})
                emojidict[retort['emoji']] += len(retort['usernames'])
        if req['deleted_by'] != 'null':
            topic_list.update({req['title']: req['like_count']})
        info('  {}/{}'.format(i+1, count))
    topic_list = sorted(topic_list.items(), key=lambda d: d[1], reverse=True)[0:3]
    info('  {}/{}'.format(i+1, count))
    return count, topic_list, retortnum, emojidict
