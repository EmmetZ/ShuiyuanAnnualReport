import json
from json.decoder import JSONDecodeError
import re
from time import sleep, time
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from typing import Union, Literal
from selenium import webdriver
import requests
from io import BytesIO
from selenium.webdriver import Edge, Chrome
from math import ceil
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


def getmUser(driver: webdriver.Edge) -> mUser:
    url = 'https://shuiyuan.sjtu.edu.cn/my/summary'
    driver.get(url)
    while 1:
        if 'u' in driver.current_url:
            break
    username = re.findall(r'https://shuiyuan.sjtu.edu.cn/u/(\S+)/summary', str(driver.current_url))
    m = getUser(driver, mode='m', username=username[0])
    return m


def getUser(driver, mode: Literal['m', 'g'], username: str) -> Union[mUser, gUser]:
    '''### Args:
        mode:\n
        'm': mUser\n
        'g': gUser
    '''
    url = USER_GROUP_URL.format(username)
    req = request(url, driver)
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
        

def pause(sec) -> None:
    for i in range(sec, 0, -1):
        sleep(1)


def isInSelectYear(utime: str, timezone: str, year: int) -> bool:
    timezone = ZoneInfo(timezone)
    ddt = datetime.strptime(utime,'%Y-%m-%dT%H:%M:%S.%fZ')
    dt = ddt.astimezone(timezone)
    if dt.year == year:
        return True
    return False


def getAvatar(user: Union[mUser, gUser], headers: dict, savepath: str):
    baseurl = SY_BASE_URL
    url = baseurl + user.avatar_template.format(size=user.avatar_size)
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
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


def request(url: str, driver: webdriver.Edge) -> dict:
    if type(driver) == Edge:
        return request_edge(url, driver)
    if type(driver) == Chrome:
        return request_chrome(url, driver)


def request_edge(url: str, driver: Edge) -> dict:
    driver.get(url)
    html = driver.page_source
    soup = bs(html, 'lxml')
    sleep(0.1)
    while 1:
        try:
            mes = soup.find('div').text
            mes = json.loads(mes)
            break
        except AttributeError as e:
            error = soup.find('pre').text
            num = int(re.findall('\d+', error)[0])
            pause(num)
            driver.get(url)
            x = driver.page_source
            soup = bs(x, 'lxml')
            continue
    return mes


def request_chrome(url: str, driver: Chrome) -> dict:
    url = 'view-source:' + url
    driver.get(url)
    html = driver.page_source
    soup = bs(html, 'lxml')
    sleep(0.1)
    while 1:
        try:
            mes = soup.find('td', attrs={'class': 'line-content'}).text
            mes = json.loads(mes)
            break
        except JSONDecodeError as e:
            errors = soup.find_all('td', attrs={'class': 'line-content'})
            for error in errors:
                try:
                    num = int(re.findall('\d+', error.text)[0])
                    break
                except:
                    continue
            pause(num)
            driver.get(url)
            x = driver.page_source
            soup = bs(x, 'lxml')
            sleep(0.1)
            continue
    return mes


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


def isRedirect(driver, refresh=False, timeout=None) -> bool:
    element = EC.url_changes(SY_BASE_URL)
    i = 0
    t = time()
    while i < 3:
        sleep(0.5)
        if refresh:
            driver.refresh()
            i += 1
        flag = not(element(driver)) and (time()-t < timeout) if timeout != None else not(element(driver)) # 判断是否重定向
        if flag:
            return True
    return False

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

