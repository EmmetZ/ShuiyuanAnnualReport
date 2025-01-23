from utils import year_of_posting, MainUser, request, get_user, flush_print
from typing import Literal, Union
from tqdm import tqdm

from utils.url import get_like_url


def get_like(
    MainUser: MainUser, headers: dict, year, filter: Literal[1, 2]
) -> Union[tuple[int, int, list], tuple[int, list]]:
    """### Args
    filter:\n
    1: like\n
    2: be liked
    """
    flag = 0
    offset = 0
    count = 0
    like_user_list = {}
    actday = []
    base_url = get_like_url(MainUser.username, str(filter))

    match filter:
        case 1:
            name = "username"
        case 2:
            name = "acting_username"
    while 1:
        url = base_url + "&offset={}".format(offset)
        req = request(url, headers)
        user_actions = req["user_actions"]
        if year < year_of_posting(user_actions[-1]["created_at"], MainUser.timezone):
            offset += 5000
            flush_print(f"skip {offset - 5000}-{offset}")
            continue
        for act in user_actions:
            if year == year_of_posting(act["created_at"], MainUser.timezone):
                flag = 1
                break
            offset += 1
        if flag:
            break

    flag = 0
    i = 0
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
                if act[name] not in like_user_list:
                    like_user_list.update({act[name]: 0})
                like_user_list[act[name]] += 1

                if filter == 1:
                    time = act["created_at"][:10].split("-")
                    time = time[1] + time[2]
                    if time not in actday:
                        actday.append(time)
                pbar.update(1)
        if flag or len(user_actions) < 5000:
            break
    like_user_list = sorted(like_user_list.items(), key=lambda d: d[1], reverse=True)[
        0:3
    ]
    top3 = []
    for i in range(len(like_user_list)):
        user = get_user(headers=headers, mode="g", username=like_user_list[i][0])
        top3.append((user, like_user_list[i][1]))
    if filter == 1:
        return count, len(actday), top3
    return count, top3
