from pathlib import Path
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw
from dataclasses import dataclass
from typing import Union, Literal
import requests
from aiohttp import ClientSession
import asyncio
from io import BytesIO
from utils.constant import SY_BASE_URL
from utils.url import get_user_group_url


@dataclass(frozen=True)
class User:
    username: str
    name: str
    avatar_template: str
    avatar_size: int = 288


@dataclass(frozen=True)
class MainUser:
    id: int
    username: str
    name: str
    avatar_template: str
    title: str
    cakeday: str
    avatar_size: int = 288
    timezone: str = "Asia/Shanghai"

    def __repr__(self):
        return (
            f"MainUser:\n"
            f"  id={self.id}\n"
            f"  username={self.username}\n"
            f"  name={self.name}\n"
            f"  avatar_template={self.avatar_template}\n"
            f"  title={self.title}\n"
            f"  cakeday={self.cakeday}\n"
            f"  avatar_size={self.avatar_size}\n"
            f"  timezone={self.timezone}\n"
        )


def get_main_user(username, headers) -> MainUser:
    return get_user(headers, mode="m", username=username)


def get_user(headers, mode: Literal["m", "g"], username: str) -> MainUser | User:
    """### Args:
    mode:\n
    'm': main user\n
    'g': general user
    """
    url = get_user_group_url(username)
    req = request(url, headers)
    memlist = req["members"]
    user = {}
    for u in memlist:
        if u["username"] == username:
            user = u
            break
    match mode:
        case "m":
            mainuser = MainUser(
                id=user["id"],
                username=user["username"],
                name=user["name"],
                avatar_template=user["avatar_template"],
                title=user["title"],
                cakeday=user["added_at"],
                timezone=user["timezone"],
            )

            return mainuser

        case "g":
            guser = User(
                username=user["username"],
                name=user["name"],
                avatar_template=user["avatar_template"],
            )
            return guser


def year_of_posting(utime: str, timezone: str) -> int:
    tz = ZoneInfo(timezone)
    ddt = datetime.strptime(utime, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=ZoneInfo("UTC")
    )
    dt = ddt.astimezone(tz)
    return dt.year


def get_avatar(user: Union[MainUser, User], headers: dict, savepath: Path):
    base_url = SY_BASE_URL
    url = base_url + user.avatar_template.format(size=user.avatar_size)
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
        sleep(1)
        req = requests.get(url, headers=headers)

    tmp = Image.open(BytesIO(req.content))
    x, y = tmp.size
    draw = ImageDraw.Draw(tmp)
    alpha_layer = Image.new("L", (x, y), 0)
    draw = ImageDraw.Draw(alpha_layer)
    draw.ellipse((0, 0, x, y), fill=255)
    img = Image.new("RGBA", (x, y), 255)
    img.paste(tmp, (0, 0), alpha_layer)
    img.save(savepath.joinpath("{}.png".format(user.username)))


def get_emoji(name, url, headers: dict, savepath: Path):
    req = requests.get(url, headers=headers)
    while req.status_code != 200:
        if req.status_code == 404:
            raise Exception("Emoji Not Found")
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            break
    img = Image.open(BytesIO(req.content))
    img.save(savepath.joinpath("{}.png".format(name)))


def request(url: str, headers: dict) -> dict:
    req = requests.get(url, headers=headers)
    # while req.status_code != 200:
    #     sleep(1)
    #     req = requests.get(url, headers=headers)
    if req.status_code != 200:
        raise Exception(f"Request Error: {req.status_code}, {req.text}")
    return req.json()


async def req_single(url: str, session: ClientSession) -> dict:
    async with session.get(url) as req:
        return await req.json()


async def async_req(url_list: str, header: dict):
    async with ClientSession(headers=header) as session:
        tasks = [req_single(url, session) for url in url_list]
        return await asyncio.gather(*tasks)


def read_cookie(path: Path) -> str:
    with open(path, "r") as f:
        cookie = f.read().strip("\n")
    return cookie


def info(msg: str):
    print(f"\033[32m{msg}\033[0m")


def flush_print(msg: str):
    print(f"\r{msg}", end="")
