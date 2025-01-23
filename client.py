import json
from pathlib import Path
from collections import Counter
import shutil
from utils import get_main_user, get_user, info
from modules.pr import (
    get_post,
    get_top_posting_day,
    get_day_dist,
    get_month_dist,
    get_id_dict,
    get_details,
    get_reply,
)
from modules import like
from modules import topic
from modules.report import Postdata, Likedata, Topicdata, WCdata, Emojidata, Report
from modules.wc import generate_wc
from utils.constant import (
    BASE_FILEPATH,
    AVATAR_PATH,
    IMG_PATH,
    RESULT_DIR,
    WORD_PATH,
)


class Client:
    def __init__(self, main_user: str, year: int) -> None:
        self.main_user = main_user
        self.year = year

    def _create_dataclass(self):
        self.PD = Postdata
        self.LD = Likedata
        self.TD = Topicdata
        self.WD = WCdata
        self.ED = Emojidata

    def get_post_data(self):
        postlist = get_post(self.main_user, self.header, self.year)
        self.PD["post"] = len(postlist)
        self.PD["actday"], self.PD["topPostingDay"] = get_top_posting_day(postlist)
        self.PD["daylist"] = get_day_dist(postlist)
        self.PD["monlist"] = get_month_dist(postlist)
        post_id_dict = get_id_dict(postlist)
        self.PD["topic"] = post_id_dict
        (
            self.PD["reply_user"],
            self.ED["retortnum"],
            self.ED["emojilist"],
            self.ED["user"],
        ) = get_details(post_id_dict, self.header, self.main_user.username)
        self.ED["ncol"] = 6
        del post_id_dict
        self.PD["reply"], self.PD["replied_user"] = get_reply(
            self.main_user, self.header, self.year
        )

    def get_like_data(self):
        info("正在获取点赞信息")
        self.LD["send"], self.LD["actday"], self.LD["like_user"] = like.get_like(
            self.main_user, self.header, self.year, filter=1
        )
        self.LD["receive"], self.LD["liked_user"] = like.get_like(
            self.main_user, self.header, self.year, filter=2
        )

    def get_topic_data(self):
        (
            self.TD["num"],
            self.TD["topic_list"],
            retortnum,
            emoji_dict,
            emoji_user_dict,
        ) = topic.get_topic(self.main_user, self.header, self.year)
        self.ED["retortnum"] += retortnum
        self.ED["emojilist"] = sorted(
            dict(Counter(self.ED["emojilist"]) + Counter(emoji_dict)).items(),
            key=lambda d: d[1],
            reverse=True,
        )[0:18]
        self.ED["user"] = dict(Counter(self.ED["user"]) + Counter(emoji_user_dict))

    def get_emoji_data(self):
        info("正在获取表情信息")
        if self.ED["user"].__contains__(self.main_user.username):
            del self.ED["user"][self.main_user.username]
        self.ED["user"] = sorted(
            self.ED["user"].items(), key=lambda d: d[1], reverse=True
        )[0:3]
        top3 = []
        for i in range(len(self.ED["user"])):
            user = get_user(
                headers=self.header, mode="g", username=self.ED["user"][i][0]
            )
            top3.append((user, self.ED["user"][i][1]))
        self.ED["user"] = top3

    def get_wordcloud(self):
        if self.PD["post"] > 0:
            info("开始生成wordcloud")
            self.WD["WCpath"] = generate_wc()
        else:
            self.WD["WCpath"] = None

    def load_custom_emoji(self):
        with BASE_FILEPATH.joinpath("resources", "custom_emoji.json").open(
            encoding="utf-8"
        ) as f:
            self.ED["custom_emoji"] = json.load(f)

    def get_all_data(self):
        self._create_dataclass()
        self.get_post_data()
        self.get_like_data()
        self.get_topic_data()
        self.get_emoji_data()
        self.get_wordcloud()
        self.load_custom_emoji()

    def load_data(self):
        self.Report = Report(self.main_user, self.year, self.header)
        userdata = {"pactday": self.PD["actday"], "lactday": self.LD["actday"]}
        self.Report.load_data("user", userdata)
        name = ["post", "like", "topic", "emoji", "wc"]
        datalist = [self.PD, self.LD, self.TD, self.ED, self.WD]
        for i in range(5):
            self.Report.load_data(name[i], datalist[i])

    def generate_report(self, year):
        if AVATAR_PATH.exists():
            shutil.rmtree(AVATAR_PATH)
        Path(AVATAR_PATH).mkdir()
        if IMG_PATH.exists():
            shutil.rmtree(IMG_PATH)
        IMG_PATH.mkdir()
        if not RESULT_DIR.exists():
            RESULT_DIR.mkdir()
        if WORD_PATH.exists():
            WORD_PATH.unlink()
        f = WORD_PATH.open("x", encoding="utf-8")
        f.close()
        self.year = year
        self.get_all_data()
        info("开始生成报告...")
        self.load_data()
        result = RESULT_DIR.joinpath(
            f"{self.main_user.username}的{self.year}年度总结.png"
        )
        self.Report.generate_report(result)
        shutil.rmtree(AVATAR_PATH)
        shutil.rmtree(IMG_PATH)
        info("完成！请在results文件夹中查看")

    def get_main_user(self):
        self.main_user = get_main_user(self.main_user, self.header)
        # print(self.main_user)
        return (self.main_user.username, self.main_user.name)

    def save_cookie(self, cookie: str, name="_t"):
        self.header = {
            "Cookie": name + "=" + cookie,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }
