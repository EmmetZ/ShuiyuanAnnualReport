from pathlib import Path
import sys

BASE_FILEPATH = Path(__file__).parent.parent.resolve()

SY_BASE_URL = "https://shuiyuan.sjtu.edu.cn/"
SY_LOGIN_URL = "https://shuiyuan.sjtu.edu.cn/login"

AVATAR_PATH = BASE_FILEPATH.joinpath("resources", "avatar_template")
WORD_PATH = BASE_FILEPATH.joinpath("results", "words.txt")
IMG_PATH = BASE_FILEPATH.joinpath("resources", "img")
DS_PATH = BASE_FILEPATH.joinpath("resources", "data")
FONT_PATH = BASE_FILEPATH.joinpath("resources", "Font")
IMG_PATH = BASE_FILEPATH.joinpath("resources", "img")
ICON_PATH = BASE_FILEPATH.joinpath("resources", "icon")
if getattr(sys, "frozen", False) and hasattr(
    sys, "_MEIPASS"
):  # 判断是否是打包后的exe文件在运行
    RESULT_DIR = BASE_FILEPATH.parent.joinpath(
        "results"
    )  # 如果是就多一层跳出_internal文件夹()
else:
    RESULT_DIR = BASE_FILEPATH.joinpath("results")
