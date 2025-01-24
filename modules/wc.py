# encoding=utf-8
from os import fspath
import jieba
from wordcloud import WordCloud
from bs4 import BeautifulSoup as bs
from utils.constant import BASE_FILEPATH, RESULT_DIR, FONT_PATH, WORD_PATH


def generate_wc() -> str:
    stopwords = []
    with BASE_FILEPATH.joinpath("resources", "stopwords.txt").open(
        "r", encoding="utf-8"
    ) as f:
        for line in f:
            stopwords.append(line.strip())

    wc = WordCloud(
        # color_func=lambda *args, **kwargs: (255,0,0),
        background_color=None,
        mode="RGBA",
        width=1600,
        height=800,
        font_path=fspath(FONT_PATH.joinpath("FZJingHJW.ttf")),
        stopwords=stopwords,
        min_font_size=8,
    )
    with WORD_PATH.open("r", encoding="utf-8") as f:
        string = f.read()
    WC = wc.generate_from_text(string)  # 绘制图片
    path = RESULT_DIR.joinpath("wordcloud.png")
    img = WC.to_image()
    img.save(path)
    return path


def extract(text: str):
    text_xml = bs(text, "html.parser")

    tag = text_xml.find_all("aside")
    for _ in range(len(tag)):
        try:
            text_xml.aside.decompose()
        except:
            break
    tag = text_xml.find_all("img")
    for _ in range(len(tag)):
        try:
            text_xml.img.decompose()
        except:
            break
    tag = text_xml.find_all("a")
    for _ in range(len(tag)):
        try:
            text_xml.a.decompose()
        except:
            break
    tag = text_xml.find_all("code")
    for _ in range(len(tag)):
        try:
            text_xml.code.decompose()
        except:
            break
    tag = text_xml.find_all("span")
    for _ in range(len(tag)):
        try:
            text_xml.span.decompose()
        except:
            break
    p = text_xml.find_all("p")
    result = ""
    for text in p:
        if len(text) > 0:
            tmp = ""
            for phrase in text:
                phrase = phrase.get_text()
                tmp += phrase.strip()

            seg_list = jieba.lcut(tmp, cut_all=False)
            string = " ".join(seg_list)
            result += string
    with WORD_PATH.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write(result)
