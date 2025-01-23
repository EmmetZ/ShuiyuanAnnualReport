import asyncio
from time import sleep

from tqdm import tqdm

from modules.wc import extract
from utils import MainUser, async_req, flush_print, info, request, year_of_posting
from utils.url import get_topic_url, get_topic_url_by_id


def get_topic(
    MainUser: MainUser, headers: dict, year
) -> tuple[int, list, int, dict, dict]:
    info("正在获取话题信息")
    flag = 0
    offset = 0
    count = 0
    topic_id_list = list()

    topic_list = dict()
    emojinum = 0
    emoji_dict = {}
    emoji_user_dict = {}
    url_list = []

    base_url = get_topic_url(MainUser.username)
    while 1:
        url = base_url + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        if len(user_actions) == 0:
            break
        if year < year_of_posting(user_actions[-1]["created_at"], MainUser.timezone):
            flush_print(f"skip {offset - 1000}-{offset}")
            offset += 1000
            continue
        for act in user_actions:
            if year == year_of_posting(act["created_at"], MainUser.timezone):
                flag = 1
                break
            offset += 1
        if flag:
            break

    if flag == 0:
        return count, topic_list, emojinum, emoji_dict, emoji_user_dict

    flag = 0
    while 1:
        url = base_url + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        with tqdm(total=len(user_actions)) as pbar:
            for act in user_actions:
                if year > year_of_posting(act["created_at"], MainUser.timezone):
                    flag = 1
                    break
                count += 1
                offset += 1
                topic_id_list.append(act["topic_id"])
            pbar.update(1)
        if flag or len(user_actions) < 1000:
            break

    for id in topic_id_list:
        url_list.append(get_topic_url_by_id(id))
    for i in range(0, len(url_list), 20):
        sub_list = url_list[i : i + 20]
        data = asyncio.run(async_req(sub_list, headers))
        for req in data:
            try:
                if req["post_stream"]["posts"][0]["cooked_hidden"] == "true":
                    pass
            except:
                extract(req["post_stream"]["posts"][0]["cooked"])
            if len(req["post_stream"]["posts"][0]["retorts"]) > 0:
                for retort in req["post_stream"]["posts"][0]["retorts"]:
                    emojinum += len(retort["usernames"])
                    if retort["emoji"] not in emoji_dict:
                        emoji_dict.update({retort["emoji"]: 0})
                    emoji_dict[retort["emoji"]] += len(retort["usernames"])
                    for user in retort["usernames"]:
                        if user not in emoji_user_dict:
                            emoji_user_dict.update({user: 0})
                        emoji_user_dict[user] += 1
            if req["deleted_by"] != "null":
                topic_list.update({req["title"]: req["like_count"]})
        # info("  {}/{}".format(i + 20 if (i + 20) <= count else count, count))
        sleep(1)

    topic_list = sorted(topic_list.items(), key=lambda d: d[1], reverse=True)[0:3]
    # info("  {}/{}".format(i + 1, count))
    return count, topic_list, emojinum, emoji_dict, emoji_user_dict
