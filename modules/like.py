from utils import *
from typing import Literal, Union
from utils.constant import  USER_LIKE_URL
from selenium import webdriver
from flet import Text, Page


def getLike(MainUser: mUser, 
            driver: Union[webdriver.Edge, webdriver.Chrome], 
            year, 
            info,
            filter: Literal[1, 2]) -> Union[tuple[int, int, list], tuple[int, list]]:
    '''### Args
        filter:\n
        1: like\n
        2: be liked
    
    '''

    flag = 0
    offset = 0
    count = 0
    like_user_list = {}
    actday = []
    info(update='nl')
    baseurl = USER_LIKE_URL.format(MainUser.username, str(filter))

    match filter:
        case 1: name = 'username'
        case 2: name = 'acting_username'
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
    i = 0
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
            if act[name] not in like_user_list:
                like_user_list.update({act[name]: 0})
            like_user_list[act[name]] += 1

            if filter == 1:
                time = act['created_at'][:10].split('-')
                time = time[1] + time[2]
                if time not in actday:
                    actday.append(time)
        if flag: break
    info('  {}'.format(count))
    like_user_list = sorted(like_user_list.items(), key=lambda d: d[1], reverse=True)[0:3]
    top3 = []
    for i in range(len(like_user_list)):
        user = getUser(driver=driver, mode='g', username=like_user_list[i][0])
        top3.append((user, like_user_list[i][1]))
    if filter == 1:
        return count, len(actday), top3
    return count, top3



            