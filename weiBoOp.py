# coding=utf-8

import json
import os
import random
import sys
import time
import traceback

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
            with open('cookies.json', 'w') as file_handler:
                file_handler.write(json_cookies)
            self.do_op()
        except TimeoutException:
            traceback.print_exception(*sys.exc_info())
            print("超过等待时间")
            print("cookie存在，但是无效，需要重新登录")
            if os.path.isfile("cookies.json"):
                os.remove("cookies.json")
            self.driver.quit()


    def do_op(self):
        self.driver.get('https://m.weibo.cn/')

        # 删除第一次建立连接时的cookie
        self.driver.delete_all_cookies()
        # 读取登录时存储到本地的cookie
        with open('cookies.json', 'r', encoding='utf-8') as file_handler:
            list_cookies = json.loads(file_handler.read())
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
        if self.commentMode == 1:  # 模式1为搜索
            self.search_comment()
        elif self.commentMode == 2:  # 模式2为热门
            self.hot_wei_bo_comment()
        elif self.commentMode == 3:  # 模式3为话题
            self.huati_comment()

    # 判断节点是否存在
    def is_element_exist(self, select_type, css):
        if select_type == "xpath":
            s = self.driver.find_elements_by_xpath(css)
        else:
            s = self.driver.find_elements_by_css_selector(css)

        if len(s) == 0:
            print("元素未找到:%s" % css)
            return False
        elif len(s) == 1:
            print("找到了")
            return True
        else:
            print("找到%s个元素：%s" % (len(s), css))
            return False

    # 处理没有找到节点的问题
    def handler_no_such_element_exception(self, by_which, value):
        if by_which == "xpath":
            print("尝试找xpath路径")
            try:
                return self.driver.find_element_by_xpath(value)
            except NoSuchElementException:
                traceback.print_exception(*sys.exc_info())
                print("没有找到节点，准备移动。错误内容：")
                self.move_page(1)
                WebDriverWait(self.driver, 15, 0.5).until(EC.presence_of_element_located((By.XPATH, value)))
                print("找到了")
                return self.driver.find_element_by_xpath(value)
            except WebDriverException:
                traceback.print_exception(*sys.exc_info())
                print("没有找到节点，准备移动")
                self.move_page(1)
                return self.driver.find_element_by_xpath(value)
        else:
            print("尝试找css_selector路径路径")
            try:
                return self.driver.find_element_by_css_selector(value)
            except NoSuchElementException:
                traceback.print_exception(*sys.exc_info())
                print("没有找到节点，准备移动。错误内容：")
                self.move_page(1)
                WebDriverWait(self.driver, 15, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, value)))
                print("找到了")
                return self.driver.find_element_by_css_selector(value)
            except WebDriverException:
                traceback.print_exception(*sys.exc_info())
                print("没有找到节点，准备移动。错误内容：")
                self.move_page(1)
                return self.driver.find_element_by_css_selector(value)

    # 处理点击找不到的问题
    def handler_click_unable(self, element_target):
        try:
            element_target.click()
        except NoSuchElementException:
            traceback.print_exception(*sys.exc_info())
            print("点击时无法点击，错误信息为：")
            time.sleep(2)
            element_target.click()
        except WebDriverException:
            traceback.print_exception(*sys.exc_info())
            print("点击时无法点击，错误信息为：")
            time.sleep(2)
            element_target.click()

    # 处理弹框
    def handler_alert(self, sleep_time=300):
        self.handler_click_unable(self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'))
        print("弹框确定")
        self.countAlert += 1
        if self.countAlert > 5:
            print("发博太多了，暂停时间：%s秒" % str(sleep_time))
            time.sleep(sleep_time)

        if self.is_element_exist("xpath", '//*[@id="app"]/div[1]/div/header/div[1]'):
            print("尝试关闭")
            self.handler_click_unable(self.handler_no_such_element_exception("xpath", '//*[@id="app"]/div[1]/div/header/div[1]'))
            print("关闭评论")

        if self.is_element_exist('css_selector','#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div'):
            print("尝试返回")
            find_element = self.handler_no_such_element_exception('css_selector','#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
            self.handler_click_unable(find_element)
            print("已返回")

    # 移动鼠标
    def move_page(self, height):
        time.sleep(2)
        if height == 0:    # 0表示移动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif height == 1:  # 表示默认移动距离
            self.driver.execute_script("window.scrollTo(0, 50);")
        print("执行了移动鼠标")

    # 发表评论
    def write_comment(self, word):
        time.sleep(1)
        self.driver.find_element_by_tag_name("textarea").send_keys(random.choice(word))  # 评论内容
        print("已发表评论")
        self.handler_click_unable(self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/header/div[3]/a'))
        print("已发送评论")

    # 搜索关键字
    def search_comment(self):
        try:
            print("开始查找发现按钮")
            WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, '发现')))
            self.handler_click_unable(self.driver.find_element_by_class_name("iconf_navbar_search"))  # 搜索按钮
            self.driver.find_element_by_class_name("forSearch").send_keys(self.findKeyWord + Keys.RETURN)  # 搜索文字
            self.op_packing()
        except NoSuchElementException:
            traceback.print_exception(*sys.exc_info())
            print("search_comment 抛出的异常：")
            print("cookies存在，但是过期了")
            self.write_to_cookie_file()
        except TimeoutException:
            traceback.print_exception(*sys.exc_info())
            WeiBoOpClass.waitLoginNum += 1
            if WeiBoOpClass.waitLoginNum % 2 == 1:
                print("cookie无效，需要重新登录")
                self.write_to_cookie_file()
            elif WeiBoOpClass.waitLoginNum % 2 == 0:
                print("search_comment 抛出的异常：", e)
                print("进入到了其他界面,即将重新打开页面")
                self.driver.quit()

    # 热门微博
    def hot_wei_bo_comment(self):
        self.handler_click_unable(self.driver.find_element_by_link_text('发现'))  # 发现按钮
        self.handler_click_unable(self.driver.find_element_by_css_selector('.card.card4.line-around'))  # 热门微博按钮

    # 话题
    def huati_comment(self):
        self.search_comment()
        self.handler_click_unable(self.handler_no_such_element_exception("xpath", '//*[@id="app"]/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div/ul/li[10]'))

    # 休息时间
    def start_sleep(self):
        print("开始休息%d秒" % int(self.timeSleep))
        time.sleep(int(self.timeSleep))  # 防止发博太快了
        print("休息结束")

    # 再次查找元素
    def find_node_again(self, css, parent=None):
        from_driver = self.driver
        if parent:
            from_driver = parent
        WebDriverWait(from_driver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, css)))
        print("等待节点，并找到了")
        try:
            WebDriverWait(from_driver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, css)))
            return from_driver.find_element_by_xpath(css)
        except StaleElementReferenceException as ex:
            traceback.print_exception(*sys.exc_info())
            print("抛出异常，重新找节点")
            return from_driver.find_element_by_xpath(css)

    def real_op(self, start_index):
        commend_list = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
        print(len(commend_list))
        if len(commend_list) == 0:
            self.move_page(0)
        for i in range(start_index, len(commend_list)):
            print("-----------------" + str(i) + "-----------------")
            # 避免发博太多导致的限制。
            time.sleep(3)
            # 下面重新获取"转发，评论，赞" 是因为进行下面一系列操作之后，返回到主页面时，内容已经改变，所以需要重新获取
            new_commend_list = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
            try:
                out_comment_btn = new_commend_list[i].find_elements_by_css_selector(".m-diy-btn.m-box-col.m-box-center.m-box-center-a")[1]

                try:
                    out_comment_btn.click()  # 外部评论
                except WebDriverException:
                    traceback.print_exception(*sys.exc_info())
                    self.move_page(1)
                    out_comment_btn.click()

                print("已点击外部评论")
                # 只有小于1条的评论，直接写入评论
                if not self.is_element_exist("xpath",
                                             '// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]'):
                    print("处理小于1条评论的情况")
                    self.write_comment(self.commentSet)
                    # 弹框处理
                    if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                        self.handler_alert()
                        self.start_sleep()
                        continue
                    self.start_sleep()
                    continue

                time.sleep(1)
                self.find_node_again(
                    '// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]').click()
                print("已点击内部评论")
                self.write_comment(self.commentSet)
                # 弹框处理
                if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                    self.handler_alert()
                    self.start_sleep()
                    continue

                if self.is_element_exist("xpath", '//*[@id="app"]/div[1]/div/div[1]/div/div[1]/div'):
                    back_btn = self.driver.find_element_by_css_selector(
                        '#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
                    self.handler_click_unable(back_btn)
                    print("已返回")
                self.start_sleep()

            except IndexError:
                traceback.print_exception(*sys.exc_info())
                print("越界了，i的值为%d, newCommendlist的长度为%d" % (i, len(new_commend_list)))
                break

        return len(commend_list)

    def op_number(self, last_do_number,start_num):
        print("开始执行第%d次" % (last_do_number + 1))
        return self.real_op(start_num)

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


getUrl = "https://m.weibo.cn/"
keyWord = "坤坤"
commentMode = 1
commendSet = ("嗯嗯","呜呜")
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

while True:
    classDriver = WeiBoOpClass(webdriver.Chrome(), keyWord, commendSet, commentMode, timeSleep)
    try:
        classDriver.start_op(getUrl)
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
    finally:
        timeSleepTime = 10
        print("------------防止发博太快，暂停%d秒----------------" % timeSleepTime)
        print("即将重新运行")
        time.sleep(timeSleepTime)
        if classDriver.driver:
            classDriver.driver.quit()

