from time import sleep
from typing import Literal
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
from modules.wc import extract
from utils import (
    MainUser,
    get_user,
    request,
    async_req,
    year_of_posting,
    info,
    flush_print,
)
from urllib.parse import urlencode
from utils.url import get_post_url, get_post_url_by_id, get_reply_url
from tqdm import tqdm


class Post:
    __timezone = None

    @classmethod
    def setTimezone(cls, timezone):
        cls.__timezone = timezone

    def __init__(
        self, topic_id: int, post_id: int, category_id: int, time: str, topic_title: str
    ) -> None:
        self.topic_id = topic_id
        self.post_id = post_id
        self.category_id = category_id
        self.time = time
        self.topic_title = topic_title

    def getTime(self, unit: Literal["year", "mon", "day", "hour"]) -> int:
        timezone = ZoneInfo(self.__timezone)
        ddt = datetime.strptime(self.time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=ZoneInfo("UTC")
        )
        dt = ddt.astimezone(timezone)
        match unit:
            case "year":
                return dt.year
            case "mon":
                return dt.month
            case "day":
                return dt.day
            case "hour":
                return dt.hour


def get_post(MainUser: MainUser, headers: dict, year) -> list:
    info("正在获取发帖信息")
    Post.setTimezone(MainUser.timezone)
    flag = 0
    offset = 0
    count = 0
    post_list = []

    baseurl = get_post_url(MainUser.username)
    timezone = MainUser.timezone

    while 1:
        url = baseurl + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        if year < year_of_posting(user_actions[-1]["created_at"], timezone):
            offset += 1000
            flush_print(f"skip {offset - 1000}-{offset}")
            continue
        for act in user_actions:
            if year == year_of_posting(act["created_at"], timezone):
                flag = 1
                break
            offset += 1
        if flag:
            break

    flag = 0
    while 1:
        url = baseurl + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        with tqdm(total=len(user_actions)) as pbar:
            for act in user_actions:
                if year > year_of_posting(act["created_at"], timezone):
                    flag = 1
                    break
                count += 1
                offset += 1
                post = Post(
                    topic_id=act["topic_id"],
                    post_id=act["post_id"],
                    category_id=act["category_id"],
                    time=act["created_at"],
                    topic_title=act["title"],
                )
                post_list.append(post)
                pbar.update(1)
        if flag or len(user_actions) < 1000:
            break
    return post_list


def get_reply(MainUser: MainUser, headers: dict, year) -> tuple[int, list]:
    info("正在获取回帖信息")
    flag = 0
    offset = 0
    count = 0
    reply_user_list = {}
    baseurl = get_reply_url(MainUser.username)

    while 1:
        url = baseurl + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        if year < year_of_posting(user_actions[-1]["created_at"], MainUser.timezone):
            offset += 1000
            flush_print(f"skip {offset - 1000}-{offset}")
            continue
        for act in user_actions:
            if year == year_of_posting(act["created_at"], MainUser.timezone):
                flag = 1
                break
            offset += 1
        if flag:
            break

    flag = 0
    while 1:
        url = baseurl + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        with tqdm(total=len(user_actions)) as pbar:
            for act in user_actions:
                if year > year_of_posting(act["created_at"], MainUser.timezone):
                    flag = 1
                    break
                count += 1
                offset += 1
                if act["username"] not in reply_user_list:
                    reply_user_list.update({act["username"]: 0})
                reply_user_list[act["username"]] += 1
                pbar.update(1)
        if flag or len(user_actions) < 1000:
            break

    reply_user_list = sorted(reply_user_list.items(), key=lambda d: d[1], reverse=True)[
        0:3
    ]
    top3 = list()
    for i in range(len(reply_user_list)):
        user = get_user(headers=headers, mode="g", username=reply_user_list[i][0])
        top3.append((user, reply_user_list[i][1]))
    return count, top3


def get_top_posting_day(post_list: list[Post]) -> tuple[int, list]:
    daydict = {}

    for post in post_list:
        day = "{}.{}".format(post.getTime("mon"), post.getTime("day"))
        if day not in daydict:
            daydict.update({day: 0})
        daydict[day] += 1

    daydict = sorted(daydict.items(), key=lambda d: d[1], reverse=True)
    Topday = []
    Max = daydict[0][1]
    for item in daydict:
        if item[1] == Max:
            Topday.append(item)
        else:
            break
    return len(daydict), Topday


def get_day_dist(post_list: list[Post]) -> list:
    period = [0 for _ in range(24)]
    for post in post_list:
        period[post.getTime("hour")] += 1
    return period


def get_month_dist(post_list: list[Post]) -> list:
    mon = [0 for _ in range(12)]
    for post in post_list:
        mon[post.getTime("mon") - 1] += 1
    return mon


def get_id_dict(post_list: list[Post]) -> dict:
    x = {}
    for item in post_list:
        if item.topic_id not in x:
            x.update({item.topic_id: {"topic_title": item.topic_title, "posts_id": []}})
        x[item.topic_id]["posts_id"].append(item.post_id)
    x = dict(sorted(x.items(), key=lambda d: len(d[1]["posts_id"]), reverse=True))
    return x


def get_details(x: dict[list], headers: dict, my) -> tuple[list, int, dict, dict]:
    """
    x = {
        topic_id: {
            'topic_title': str,
            'posts_id': list
    }
    """
    reply_user_dict = {}
    emojinum = 0
    emoji_dict = {}
    emoji_user_dict = {}
    url_list = make_url_list(x)
    total = len(url_list)
    M = 5
    for i in range(0, total, M):
        sub_list = url_list[i : i + M]
        posts = []
        data = asyncio.run(async_req(sub_list, headers))
        for item in data:
            posts.extend(item["post_stream"]["posts"])
        del data
        for post in posts:
            extract(post["cooked"])
            if post.__contains__("reply_to_user"):
                pr = post["reply_to_user"]
                if (pr["username"] not in reply_user_dict) and pr["username"] != my:
                    reply_user_dict.update({pr["username"]: 0})
                if pr["username"] != my:
                    reply_user_dict[pr["username"]] += 1
            # 计算贴表情
            if len(post["retorts"]) > 0:
                for retort in post["retorts"]:
                    emojinum += len(retort["usernames"])
                    if retort["emoji"] not in emoji_dict:
                        emoji_dict.update({retort["emoji"]: 0})
                    emoji_dict[retort["emoji"]] += len(retort["usernames"])
                    for user in retort["usernames"]:
                        if user not in emoji_user_dict:
                            emoji_user_dict.update({user: 0})
                        emoji_user_dict[user] += 1
        del posts
        sleep(1)
    reply_user_dict = sorted(reply_user_dict.items(), key=lambda d: d[1], reverse=True)[
        0:3
    ]
    top3 = list()
    for i in range(len(reply_user_dict)):
        user = get_user(headers=headers, mode="g", username=reply_user_dict[i][0])
        top3.append((user, reply_user_dict[i][1]))

    return top3, emojinum, emoji_dict, emoji_user_dict


def make_url_list(x: dict, max: int = 500) -> list:
    url_list = []
    for item in x:
        baseurl = get_post_url_by_id(str(item))
        num = len(x[item]["posts_id"])
        flag = 1
        start = 0
        end = max
        while flag:
            url = baseurl
            if end > num:
                ids = x[item]["posts_id"][start:num]
                flag = 0
            else:
                ids = x[item]["posts_id"][start:end]
                start = end
                end += max
            for j, id in enumerate(ids):
                if j > 0:
                    url += "&"
                url += urlencode({"post_ids[]": id})
            url_list.append(url)
    return url_list
