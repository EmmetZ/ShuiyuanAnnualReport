from bs4 import BeautifulSoup
from pathlib import Path
import json

path = Path(__file__).parent

with path.joinpath("resources/custom-emoji.html").open("r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

img_tags = soup.find_all("img")
res = {}

for img in img_tags:
    res.update({img.get("title"): img.get("src")})

with path.joinpath("resources/custom_emoji.json").open("w", encoding="utf-8") as f:
    json.dump(res, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行
