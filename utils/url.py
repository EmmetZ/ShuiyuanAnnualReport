def get_post_url(username):
    return f"https://shuiyuan.sjtu.edu.cn/user_actions.json?username={username}&limit=1000&filter=5"


def get_reply_url(username):
    return f"https://shuiyuan.sjtu.edu.cn/user_actions.json?username={username}&limit=1000&filter=6"


def get_like_url(username, filter):
    return f"https://shuiyuan.sjtu.edu.cn/user_actions.json?username={username}&limit=5000&filter={filter}"


def get_topic_url(username):
    return f"https://shuiyuan.sjtu.edu.cn/user_actions.json?username={username}&limit=1000&filter=4"


def get_topic_url_by_id(id):
    return f"https://shuiyuan.sjtu.edu.cn/t/{id}.json"


def get_post_url_by_id(id):
    return f"https://shuiyuan.sjtu.edu.cn/t/{id}/posts.json?"


def get_user_group_url(filter):
    return f"https://shuiyuan.sjtu.edu.cn/groups/trust_level_0/members.json?filter={filter}&limit=1000"
