from pathlib import Path
from client import Client
import time
from utils import read_cookie


if __name__ == "__main__":
    username = input("username: ")
    default_year = int(time.strftime("%Y", time.localtime())) - 1
    flag = input(f"year: {default_year} (y/n): ")
    if flag.lower() == "y":
        year = default_year
    else:
        year = int(input("year(例: 2024 请输入 24): ")) + 2000
        if 20 > year or year > default_year:
            raise ValueError(f"年份输入错误, 20 <= input <= {default_year - 2000}")

    client = Client(username, year)
    cookie = read_cookie(Path.cwd().joinpath("cookie.txt"))
    header = client.save_cookie(cookie)
    username, name = client.get_main_user()
    print(f"用户名: {username}, 名字: {name}")
    client.generate_report(year)
