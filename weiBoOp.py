# coding=utf-8

import json
import os
import random
import sys
import time
import traceback

import wmi
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class WeiBoOpClass(object):
    # 等待登录的情况
    waitLoginNum = 0

    def __init__(self, driver, find_key_word, commend_set, comment_mode, time_sleep):
        self.driver = driver
        self.countAlert = 0
        self.findKeyWord = find_key_word
        self.commentSet = commend_set
        self.commentMode = comment_mode
        self.timeSleep = time_sleep
        self.sleep_time_for_action = 2

    # 传入地址和关键字，开始操作
    def start_op(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        self.is_have_cookies_file()

    # 判断是否有cookie文件
    def is_have_cookies_file(self):
        if os.path.isfile("cookies.json"):
            print("cookies存在，执行正常流程")
            self.do_op()
        else:
            print("cookies不存在")
            self.write_to_cookie_file()

    # 写入cookieFile
    def write_to_cookie_file(self):
        print("等待登录")
        try:
            WebDriverWait(self.driver, 300, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, '发现')))
            dict_cookies = self.driver.get_cookies()
            json_cookies = json.dumps(dict_cookies)

            # 登录完成后，将cookie保存到本地文件
            with open('cookies.json', 'w') as file_handler_write:
                file_handler_write.write(json_cookies)
            self.do_op()
        except TimeoutException:
            traceback.print_exception(*sys.exc_info())
            print("超过等待时间")
            print("cookie存在，但是无效，需要重新登录")
            if os.path.isfile("cookies.json"):
                os.remove("cookies.json")
            self.driver.quit()

    def do_op(self):
        # 删除第一次建立连接时的cookie
        self.driver.delete_all_cookies()
        # 读取登录时存储到本地的cookie
        with open('cookies.json', 'r', encoding='utf-8') as file_handler_in_do:
            list_cookies = json.loads(file_handler_in_do.read())
        for cookie_item in list_cookies:
            self.driver.add_cookie({
                'domain': '.weibo.cn',
                'name': cookie_item['name'],
                'value': cookie_item['value'],
                'path': '/',
                'expiry': None
            })
        # 再次访问页面，便可实现免登陆访问
        self.driver.get('https://m.weibo.cn/')

        # 根据模式，选择不同操作
        if self.commentMode == 1 or self.commentMode == 3:    # 模式1为搜索,模式3为超级话题
            self.search_comment()
        elif self.commentMode == 2:  # 模式2为热门
            self.hot_wei_bo_comment()

    # 判断节点是否存在
    def is_element_exist(self, select_type, css):
        start=time.time()
        if select_type == "xpath":
            s = self.driver.find_elements_by_xpath(css)
        elif select_type == 'css_selector':
            s = self.driver.find_elements_by_css_selector(css)
        elif select_type == 'class_name':
            s = self.driver.find_elements_by_class_name(css)

        if len(s) == 0:
            print("元素未找到:%s" % css)
            return False
        elif len(s) == 1:
            print("找到了")
            return True
        else:
            print("找到%s个元素：%s" % (len(s), css))
            return False


    # 处理点击找不到的问题
    def handler_click_unable(self, element_target):
        WebDriverWait(self.driver, 10, 0.5).until_not(EC.presence_of_element_located((By.CLASS_NAME, "m-mask")))
        try:
            element_target.click()
        except TimeoutException:
            traceback.print_exception(*sys.exc_info())
            print("点击时无法点击")
            time.sleep(2)
            element_target.click()
        except WebDriverException:
            traceback.print_exception(*sys.exc_info())
            print("点击时无法点击")
            time.sleep(2)
            element_target.click()

    # 等待某个节点出现在执行
    def wait_web_driver(self,search_type, value):
        try:
            if search_type == "link_text":
                WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, value)))
            elif search_type == "className":
                WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, value)))
                return self.driver.find_element_by_class_name(value)
            elif search_type == "xpath":
                WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, value)))
                return self.driver.find_element_by_xpath(value)
            elif search_type == "tag_name":
                WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.TAG_NAME, value)))
                return self.driver.find_element_by_tag_name(value)
        except TimeoutException:
            print("没有找到节点")
            self.driver.quit()

    # 处理弹框
    def handler_alert(self,alert_text, sleep_time=3600):
        self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a').click()
        print("弹框确定")
        if alert_text == "发微博太多啦，休息一会儿吧!":
            self.countAlert += 1
        if self.countAlert > 5:
            print("发博太多了，暂停时间：%s秒" % str(sleep_time))
            time.sleep(sleep_time)

        if self.is_element_exist("xpath", '//*[@id="app"]/div[1]/div/header/div[1]'):
            print("尝试关闭")
            self.handler_click_unable(self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/header/div[1]'))
            print("关闭评论")

        if self.is_element_exist('css_selector','#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div'):
            print("尝试返回")
            find_element = self.driver.find_element_by_css_selector('#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
            self.handler_click_unable(find_element)
            print("已返回")

    # 移动鼠标
    def move_page(self, height):
        time.sleep(2)
        if height == 0:    # 0表示移动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif height == 1:  # 表示默认移动距离
            self.driver.execute_script("window.scrollTo(0, 50);")
        #print("执行了移动鼠标")

    # 发表评论
    def write_comment(self, word):
        self.do_a_op_sleep()
        self.wait_web_driver("tag_name","textarea").send_keys(random.choice(word))  # 评论内容
        self.do_a_op_sleep()
        if self.is_element_exist("class_name",'m-search'):
            self.driver.find_element_by_class_name('m-search').click()
            self.driver.find_element_by_css_selector('.search-cancel.m-box-center-a').click()
            self.do_a_op_sleep()
        print("已发表评论")
        self.wait_web_driver("xpath",'//*[@id="app"]/div[1]/div/header/div[3]/a').click()
        print("已发送评论")

    # 搜索关键字
    def search_comment(self):
        try:
            print("开始查找发现按钮")
            # 这里又再找一遍 “发现按钮” 是因为可能进入到了别的界面
            WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, '发现')))
            self.wait_web_driver("className","iconf_navbar_search").click()
            self.wait_web_driver("className","forSearch").send_keys(self.findKeyWord + Keys.RETURN)  # 搜索文字
            if self.commentMode == 3:
                self.driver.find_elements_by_class_name("m-text-box")[0].click()          #  进入超级话题
                print("等待加载内容")
                time.sleep(8)
                self.driver.find_elements_by_tag_name('li')[1].click()  #  进入帖子
            try:
                self.op_packing()
            except Exception:
                traceback.print_exception(*sys.exc_info())
                #print("执行op_packing 抛出的异常")
                self.driver.quit()
        except NoSuchElementException:
            traceback.print_exception(*sys.exc_info())
            print("cookies存在，但是过期了,需要重新登录")
            self.write_to_cookie_file()
        except TimeoutException:
            traceback.print_exception(*sys.exc_info())
            WeiBoOpClass.waitLoginNum += 1
            if WeiBoOpClass.waitLoginNum % 2 == 1:
                print("cookie无效，需要重新登录")
                self.write_to_cookie_file()
            elif WeiBoOpClass.waitLoginNum % 2 == 0:
                print("进入到了其他界面,即将重新打开页面")
                self.driver.quit()

    # 热门微博
    def hot_wei_bo_comment(self):
        self.handler_click_unable(self.driver.find_element_by_link_text('发现'))  # 发现按钮
        self.handler_click_unable(self.driver.find_element_by_css_selector('.card.card4.line-around'))  # 热门微博按钮

    # 休息时间
    def op_once_sleep(self):
        print("开始休息%d秒" % int(self.timeSleep))
        time.sleep(int(self.timeSleep))  # 防止发博太快了
        print("休息结束")

    # 执行一个动作停止时间
    def do_a_op_sleep(self):
        #print("执行一个动作休息的时间%d" % self.sleep_time_for_action)
        time.sleep(self.sleep_time_for_action)  # 防止发博太快了

    # 再次查找元素
    def find_node_again(self, css):
        try:
            WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, css)))
            return self.driver.find_element_by_xpath(css)
        except StaleElementReferenceException as ex:
            traceback.print_exception(*sys.exc_info())
            self.do_a_op_sleep()
            print("等待重新找节点")
            return self.driver.find_element_by_xpath(css)

    def get_new_outer_comment_list(self,index):
        new_commend_list = self.driver.find_elements_by_tag_name("footer")
        out_comment_btn = new_commend_list[index].find_elements_by_css_selector(".m-diy-btn.m-box-col.m-box-center.m-box-center-a")[1]
        return out_comment_btn

    # 判断是否有微博内打开按钮
    def is_have_open_wei_bo_btn(self,i):
        if(self.is_element_exist("xpath",'//*[@id="app"]/div[1]/aside/a')):
            open_wei_bo_btn_pos = self.wait_web_driver("xpath", '//*[@id="app"]/div[1]/aside/a').location  # 点击打开微博按钮
            find_node_pos=self.get_new_outer_comment_list(i).location
            # print("移动前 openWeiBoBtnPos=", open_wei_bo_btn_pos)
            # print("移动前 footNode=", find_node_pos)
            while open_wei_bo_btn_pos["y"] - 100 < find_node_pos["y"]:
                self.driver.execute_script("window.scrollBy(100, %d);" % (200))
                open_wei_bo_btn_pos = self.wait_web_driver("xpath", '//*[@id="app"]/div[1]/aside/a').location
                #print("移动后 openWeiBoBtnPos=", open_wei_bo_btn_pos)
                find_node_pos = self.get_new_outer_comment_list(i).location
                #print("移动后 footNode=", find_node_pos)
                time.sleep(1)
            if open_wei_bo_btn_pos["y"]>find_node_pos["y"]:
                return True

    def real_op(self, start_index):
        commend_list = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
        print("发现 %d条 内容"%(len(commend_list)))
        if len(commend_list) == 0:
            self.move_page(0)
            commend_list = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
        if len(commend_list) == 0:
            print("没有内容，可以评论")
        for i in range(start_index, len(commend_list)):
            print("-----------------" + str(i) + "-----------------")
            # 下面重新获取"转发，评论，赞" 是因为进行下面一系列操作之后，返回到主页面时，内容已经改变，所以需要重新获取
            new_commend_list = self.driver.find_elements_by_tag_name("footer")
            try:
                out_comment_btn = new_commend_list[i].find_elements_by_css_selector(".m-diy-btn.m-box-col.m-box-center.m-box-center-a")[1]

                if self.is_have_open_wei_bo_btn(i):
                    try:
                        out_comment_btn.click()  # 外部评论
                    except WebDriverException:
                        traceback.print_exception(*sys.exc_info())
                        self.move_page(1)
                        out_comment_btn.click()
                    print("已点击外部评论")

                # 只有小于1条的评论，直接写入评论
                if not self.is_element_exist("xpath", '// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]'):
                    print("处理小于1条评论的情况")
                    self.write_comment(self.commentSet)

                    # 弹框处理
                    if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                        alert_text = self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[1]/div[2]/header/h3').text
                        self.handler_alert(alert_text)
                        self.op_once_sleep()
                        continue
                    self.op_once_sleep()
                    continue

                self.do_a_op_sleep()
                self.find_node_again(
                    '// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]').click()
                print("已点击内部评论")
                self.write_comment(self.commentSet)
                self.do_a_op_sleep()

                # 弹框处理
                if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                    alert_text = self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[1]/div[2]/header/h3').text
                    self.handler_alert(alert_text)
                    self.op_once_sleep()
                    continue

                if self.is_element_exist("xpath", '//*[@id="app"]/div[1]/div/div[1]/div/div[1]/div'):
                    back_btn = self.driver.find_element_by_css_selector(
                        '#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
                    self.handler_click_unable(back_btn)
                    print("已返回")
                self.op_once_sleep()

            except IndexError:
                traceback.print_exception(*sys.exc_info())
                print("越界了，i的值为%d, newCommendlist的长度为%d" % (i, len(new_commend_list)))
                break

        return len(commend_list)

    def op_number(self, last_do_index, last_start_num):
        print("------------------------------------")
        print("开始执行第%d次" % (last_do_index + 1))
        return self.real_op(last_start_num)

    def op_packing(self):
        last_start_index = 0
        for i in range(6):
            try:
                last_start_index = self.op_number(i, last_start_index)
            except IndexError:
                traceback.print_exception(*sys.exc_info())
                break

        print("------------执行完了，准备关闭------------")
        self.driver.quit()


#当前文件的路径
pwd = os.getcwd()+'\chromedriver.exe'
os.environ['PATH'] = os.environ['PATH'] + ';' + pwd

# 将磁盘写入到文件中
def write_disk_to_file():
    c = wmi.WMI()
    for physical_disk in c.Win32_DiskDrive():
        return physical_disk.SerialNumber


getUrl = "https://m.weibo.cn/"
keyWord = "坤坤"
commentMode = 1
commendSet = ("卡", "up","嗯@蔡徐坤","嗯嗯@蔡徐坤","嗯嗯嗯@蔡徐坤")
timeSleep = 15

if os.path.isfile("configComment.json"):
    with open('configComment.json', 'r', encoding='utf-8') as f:
        configs = json.loads(f.read())
        for cookie in configs:
            keyWord = cookie["keyWord"]
            commendSet = tuple(cookie['commentSet'])
            timeSleep = cookie["time"]
else:
    print("使用了默认配置")

if not os.path.exists('diskValue.txt'):
    with open('diskValue.txt', 'w') as file_handler:
        file_handler.write(write_disk_to_file())

if os.path.isfile('diskValue.txt'):
    diskValue = open("diskValue.txt").read()
    if diskValue != write_disk_to_file():
        print("请误外传此软件，谢谢。即将关闭")
        time.sleep(3)
        sys.exit()

while True:
    classDriver = WeiBoOpClass(webdriver.Chrome(), keyWord, commendSet, commentMode, timeSleep)
    try:
        classDriver.start_op(getUrl)
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
    finally:
        print("------------防止发博太快，暂停评论----------------")
        classDriver.op_once_sleep()
        print("即将重新运行")
        if classDriver.driver:
            classDriver.driver.quit()

