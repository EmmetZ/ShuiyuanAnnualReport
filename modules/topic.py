import asyncio
from time import sleep
from utils import *
from modules.wc import extract
from utils.constant import  USER_TOPIC_URL, TOPIC_URL



def getTopic(MainUser: mUser, headers: dict, year, info) -> tuple[int, list, int, dict, dict]:
    flag = 0
    offset = 0
    count = 0
    topic_id_list = list()
    info(update='nl')

    baseurl = USER_TOPIC_URL.format(MainUser.username)
    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, headers)
        user_actions = req['user_actions']
        if year < yearOfPosting(user_actions[-1]['created_at'], MainUser.timezone):
            offset += 1000
            continue
        for act in user_actions:
            if year == yearOfPosting(act['created_at'], MainUser.timezone):
                flag = 1
                break
            offset += 1
        if flag: break
    
    if flag == 0: 
        return 0
    
    flag = 0
    while(1):
        url = baseurl + '&offset={}'.format(offset)
        req = request(url, headers)
        user_actions = req['user_actions']
        if len(user_actions) < 1000:
            flag = 1
        for act in user_actions:
            if year > yearOfPosting(act['created_at'], MainUser.timezone):
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
    emojinum = 0
    emoji_dict = {}
    emoji_user_dict = {}
    urlList = []
    for id in topic_id_list:
        urlList.append(TOPIC_URL.format(id))
    for i in range(0, len(urlList), 20):
        subList = urlList[i:i+20]
        data = asyncio.run(asyncReq(subList, headers))
        for req in data:
            try:
                if req['post_stream']['posts'][0]['cooked_hidden'] == 'true':
                    pass
            except:
                extract(req['post_stream']['posts'][0]['cooked'])
            if len(req['post_stream']['posts'][0]['retorts']) > 0:
                for retort in req['post_stream']['posts'][0]['retorts']:
                    emojinum += len(retort['usernames'])
                    if retort['emoji'] not in emoji_dict:
                        emoji_dict.update({retort['emoji']: 0})
                    emoji_dict[retort['emoji']] += len(retort['usernames'])
                    for user in retort['usernames']:
                        if user not in emoji_user_dict:
                            emoji_user_dict.update({user: 0})
                        emoji_user_dict[user] += 1
            if req['deleted_by'] != 'null':
                topic_list.update({req['title']: req['like_count']})
        info('  {}/{}'.format(i+20 if (i+20) <= count else count, count))
        sleep(1)

    topic_list = sorted(topic_list.items(), key=lambda d: d[1], reverse=True)[0:3]
    info('  {}/{}'.format(i+1, count))
    return count, topic_list, emojinum, emoji_dict, emoji_user_dict
