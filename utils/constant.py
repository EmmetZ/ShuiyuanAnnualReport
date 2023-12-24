from pathlib import Path
import sys


USER_LIKE_URL = 'https://shuiyuan.sjtu.edu.cn/user_actions.json?username={}&limit=1000&filter={}'
USER_POST_URL = 'https://shuiyuan.sjtu.edu.cn/user_actions.json?username={}&limit=1000&filter=5'
USER_REPLY_URL = 'https://shuiyuan.sjtu.edu.cn/user_actions.json?username={}&limit=1000&filter=6'
USER_TOPIC_URL = 'https://shuiyuan.sjtu.edu.cn/user_actions.json?username={}&limit=1000&filter=4'
TOPIC_URL = 'https://shuiyuan.sjtu.edu.cn/t/{}.json'
POST_URL = 'https://shuiyuan.sjtu.edu.cn/t/{}/posts.json?'

class Browser:
    EDGE = 'edge'
    CHROME = 'chrome'

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):  # 判断是否是打包后的exe文件在运行
    BASE_FILEPATH = Path(__file__).parent.parent.parent.resolve()  # 如果是就多条一层跳出_internal文件夹()
else:
    BASE_FILEPATH = Path(__file__).parent.parent.resolve()

EDGE_DRIVER_PATH = BASE_FILEPATH.joinpath('resources', 'webdriver', 'msedgedriver.exe')
CHROME_DRIVER_PATH = BASE_FILEPATH.joinpath('resources', 'webdriver', 'chromedriver.exe')

SY_BASE_URL = 'https://shuiyuan.sjtu.edu.cn/'
SY_LOGIN_URL = 'https://shuiyuan.sjtu.edu.cn/login'

USER_GROUP_URL = 'https://shuiyuan.sjtu.edu.cn/groups/trust_level_0/members.json?filter={}&limit=1000'

AVATAR_PATH = BASE_FILEPATH.joinpath('resources', 'avatar_template')
WORD_PATH = BASE_FILEPATH.joinpath('resources', 'words.txt') 
IMG_PATH = BASE_FILEPATH.joinpath('resources', 'img')
RESULT_DIR = BASE_FILEPATH.joinpath('results')
DS_PATH = BASE_FILEPATH.joinpath('resources', 'data')
FONT_PATH = BASE_FILEPATH.joinpath('resources', 'Font')
IMG_PATH = BASE_FILEPATH.joinpath('resources', 'img')
ICON_PATH = BASE_FILEPATH.joinpath('resources', 'icon')
