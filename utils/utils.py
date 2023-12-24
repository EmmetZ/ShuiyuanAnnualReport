import re
from time import sleep, time
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from typing import Union, Literal
from selenium import webdriver
import requests
from aiohttp import ClientSession
import asyncio
from io import BytesIO
from utils.constant import SY_BASE_URL, USER_GROUP_URL, EDGE_DRIVER_PATH, CHROME_DRIVER_PATH 
from utils.constant import Browser


@dataclass(frozen=True)
class gUser:
    username: str
    name: str
    avatar_template: str
    avatar_size: int = 288


@dataclass(frozen=True)
class mUser:
    id: int
    username: str
    name: str
    avatar_template: str
    title: str
    cakeday: str
    avatar_size: int = 288
    timezone: str = 'Asia/Shanghai'


def getmUser(driver: webdriver.Edge, headers) -> mUser:
    url = 'https://shuiyuan.sjtu.edu.cn/my/summary'
    driver.get(url)
    while 1:
        if 'u' in driver.current_url:
            break
    username = re.findall(r'https://shuiyuan.sjtu.edu.cn/u/(\S+)/summary', str(driver.current_url))
    m = getUser(headers, mode='m', username=username[0])
    return m


def getUser(headers, mode: Literal['m', 'g'], username: str) -> Union[mUser, gUser]:
    '''### Args:
        mode:\n
        'm': mUser\n
        'g': gUser
    '''
    url = USER_GROUP_URL.format(username)
    req = request(url, headers)
    memlist = req['members']
    for user in memlist:
        if user['username'] == username:
            break
    match mode:
        case 'm':
            mainuser = mUser(
                            id = user['id'],
                            username = user['username'],
                            name = user['name'],
                            avatar_template = user['avatar_template'],
                            title = user['title'],
                            cakeday = user['added_at'], 
                            timezone = user['timezone'])

            return mainuser
    
        case 'g':
            guser = gUser(
                    username = user['username'],
                    name = user['name'],
                    avatar_template = user['avatar_template'])
            return guser
        

def yearOfPosting(utime: str, timezone: str) -> int:
    timezone = ZoneInfo(timezone)
    ddt = datetime.strptime(utime,'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo('UTC'))
    dt = ddt.astimezone(timezone)
    return dt.year

def getAvatar(user: Union[mUser, gUser], headers: dict, savepath: str):
    baseurl = SY_BASE_URL
    url = baseurl + user.avatar_template.format(size=user.avatar_size)
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
        sleep(1)
        req = requests.get(url, headers=headers)

    tmp = Image.open(BytesIO(req.content))
    x, y = tmp.size
    draw = ImageDraw.Draw(tmp)   
    alpha_layer = Image.new('L', (x, y), 0)
    draw = ImageDraw.Draw(alpha_layer)
    draw.ellipse((0, 0, x, y), fill=255)
    img = Image.new('RGBA', (x, y), 255)
    img.paste(tmp, (0, 0), alpha_layer)
    img.save(savepath.joinpath('{}.png'.format(user.username)))


def getEmoji(name, url, headers: dict, savepath: str):
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
        if req.status_code == 404:
            raise Exception('Emoji Not Found')
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            break
    img = Image.open(BytesIO(req.content))
    img.save(savepath.joinpath('{}.png'.format(name)))


def getWebdriver(type, headless=False):
    match type:
        case Browser.EDGE:
            service = EdgeService(EDGE_DRIVER_PATH)
            op = webdriver.EdgeOptions()
        case Browser.CHROME:
            service = ChromeService(CHROME_DRIVER_PATH)
            op = webdriver.ChromeOptions()
    op.add_experimental_option("detach" , True)
    op.add_argument("--disable-extensions")
    op.add_argument("--disable-gpu")
    op.add_argument('--no-sandbox')
    op.add_argument('--ignore-certificate-errors')
    op.add_argument("--disable-browser-side-navigation") 
    op.add_argument("--disable-infobars")
    op.add_argument('--incognito')
    op.add_argument('log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    if headless:
        op.add_argument("blink-settings=imagesEnabled=false")
        op.add_argument('headless')
    match type:
        case Browser.EDGE:
            driver = webdriver.Edge(options=op, service=service)
        case Browser.CHROME:
            driver = webdriver.Chrome(options=op, service=service)
    return driver


def request(url: str, headers: dict) -> dict:
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
        sleep(1)
        req = requests.get(url, headers=headers)
    return req.json()


def isRedirect(driver, refresh=False, timeout=None) -> bool:
    element = EC.url_changes(SY_BASE_URL)
    i = 0
    t = time()
    while i < 3:
        sleep(0.5)
        if refresh:
            driver.refresh()
            i += 1
        flag = not(element(driver))  
        if timeout != None:
            if flag and (time()-t < timeout):
                return True
            elif time()-t > timeout:
                break
        else:
            if flag:
                return True
    return False


async def reqSingle(url: str, session: ClientSession) -> dict:
    async with session.get(url) as req:
        return await req.json()    


async def asyncReq(urlList: str, headers: dict):
    session = ClientSession(headers=headers)
    tasks = [reqSingle(url ,session) for url in urlList]
    return await asyncio.gather(*tasks)
'''
def split_dict(dictionary, count) -> list[dict]:
    sub_dicts = []
    keys = list(dictionary.keys())
    total_keys = len(keys)
    x = ceil(total_keys / count)

    for i in range(count):
        start = i * x
        if (i+1)*x > total_keys-1:
            end = total_keys
        else:
            end = (i + 1) * x
        sub_dict = {k: dictionary[k] for k in keys[start: end]}
        sub_dicts.append(sub_dict)
    return sub_dicts
'''

