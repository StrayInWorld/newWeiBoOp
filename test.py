from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import json
import time

driver = webdriver.Chrome()

def waitWebDriver(type,value):
    if type=="link_text":
        WebDriverWait(driver, 300, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, value)))
    elif type=="className":
        WebDriverWait(driver, 300, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, value)))
        return driver.find_element_by_class_name(value)
    elif type=="xpath":
        WebDriverWait(driver, 300, 0.5).until(EC.presence_of_element_located((By.XPATH, value)))
        print("找到了")
        return driver.find_element_by_xpath(value)

driver.get("https://m.weibo.cn/")

# 删除第一次建立连接时的cookie
driver.delete_all_cookies()
# 读取登录时存储到本地的cookie
with open('cookies.json', 'r', encoding='utf-8') as f:
    listCookies = json.loads(f.read())
for cookie in listCookies:
    driver.add_cookie({
        'domain': '.weibo.cn',
        'name': cookie['name'],
        'value': cookie['value'],
        'path': '/',
        'expiry': None
    })
# 再次访问页面，便可实现免登陆访问
driver.get('https://m.weibo.cn/')

waitWebDriver("link_text",'发现')
waitWebDriver("className","iconf_navbar_search").click() # 搜索按钮
waitWebDriver("className","forSearch").send_keys('#蔡徐坤#' + Keys.RETURN)  # 搜索文字
waitWebDriver("xpath",'//*[@id="app"]/div[1]/div[1]/div[3]/div/div[1]').click()  # 点击超级话题
time.sleep(5)
openWeiBoBtnPos = waitWebDriver("xpath",'//*[@id="app"]/div[1]/aside/a').location  # 点击打开微博按钮
print("openWeiBoBtnPos=",openWeiBoBtnPos)

# 这里应该等某个东西出来了，再执行下面的内容，而不是强制sleep()
time.sleep(5)
footNodes=driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
footNodePos=footNodes[0].location
print("footNode",footNodePos)

srollNum=1
while openWeiBoBtnPos["y"]-200<footNodePos["y"]:
    driver.execute_script("window.scrollTo(100, %d);"%(srollNum*200))
    srollNum += 1
    openWeiBoBtnPos=waitWebDriver("xpath", '//*[@id="app"]/div[1]/aside/a').location
    print("移动后 openWeiBoBtnPos=",openWeiBoBtnPos)
    footNodePos=footNodes[0].location
    print("移动后 footNode=",footNodePos)
    time.sleep(1)


# if openWeiBoBtnPos["y"]>footNodePos["y"]:
#     footNodes[0].click()


