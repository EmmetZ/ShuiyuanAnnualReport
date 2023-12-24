from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
from pathlib import Path
from utils.constant import SY_LOGIN_URL, SY_BASE_URL, EDGE_DRIVER_PATH

path = Path(__file__).parent

service = Service(EDGE_DRIVER_PATH)
op = webdriver.EdgeOptions()
op.add_experimental_option("detach", True)
op.add_argument("--disable-extensions")
op.add_argument("--disable-gpu")
op.add_argument('--no-sandbox')
op.add_argument('--ignore-certificate-errors')
driver = webdriver.Edge(options=op, service=service)

driver.get(SY_LOGIN_URL)
driver.add_cookie({'name': '_t', 'value': ''})  # 填入cookie
driver.implicitly_wait(10)

element = EC.url_changes(SY_BASE_URL)
while 1:
    driver.refresh()
    flag = element(driver)# 判断是否重定向
    if not flag:
        break

driver.get('https://shuiyuan.sjtu.edu.cn/t/topic/205915')
xp1 = '/html/body/section/div/div[4]/div[2]/div[2]/div[3]/div[3]/section/div[1]/div[2]/div/div[1]/article/div/div[2]/div[2]/section/nav/div/span/button'
driver.execute_script('window.scrollBy(0,300)')
driver.find_element(By.XPATH, xp1).click()

req = {}
x = 0
for i in range(2, 8):
    xp = '/html/body/section/div/div[5]/div/div[2]/div[2]/div[2]/div[{}]/div[2]//span/img'.format(i)
    a = driver.find_elements(By.XPATH, xp)
    for em in a:
        req.update({em.get_attribute('title'): em.get_attribute('src')})
        x += 1
        print(f'\r{x}', flush=True, end='')
driver.quit()
with path.joinpath('resources/extra_emoji.json').open('w', encoding='utf-8') as f:
    json.dump(req, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行