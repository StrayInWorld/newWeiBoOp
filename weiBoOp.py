# coding=utf-8

import json
import os
import random
import time
import sys,traceback

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

class weiBoOpClass(object):
    def __init__(self,driver):
         self.driver=driver
         self.countAlert=0

    # 传入地址和关键字，开始操作
    def startOp(self,url,findKeyWord,commendSet,commentMode,timeSleep):
        self.findKeyWord=findKeyWord
        self.commentSet=commendSet
        self.commentMode=commentMode
        self.timeSleep=timeSleep
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        self.isHaveCookiesFile()

    # 判断是否有cookie文件
    def isHaveCookiesFile(self):
        if os.path.isfile("cookies.json"):
            print("cookies存在，执行正常流程")
            self.doOp()
        else:
            print("cookies不存在")
            self.writeToCookieFile()

    # 写入cookieFile
    def writeToCookieFile(self):
        try:
            print("等待登录")
            try:
                WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, '发现')))
                dictCookies = self.driver.get_cookies()
                jsonCookies = json.dumps(dictCookies)

            except TimeoutException:
                print("超过等待时间")
                print("cookie存在，但是无效，需要重新登录")
                if os.path.isfile("cookies.json"):
                    os.remove("cookies.json")
                    self.driver.quit()

            # 登录完成后，将cookie保存到本地文件
            with open('cookies.json', 'w') as f:
                f.write(jsonCookies)
            self.doOp()
        finally:
            self.driver.close()

    # 判断节点是否存在
    def is_element_exist(self,selectType,css):
        s=None
        if selectType=="xpath":
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
    def handlerNoSuchElementException(self,byWhich,value):
         if byWhich=="xpath":
             print("尝试找xpath路径")
             try:
                 return self.driver.find_element_by_xpath(value)
             except NoSuchElementException as e:
                 print("没有找到节点，准备移动。错误内容：",e)
                 self.movePage(1)
                 WebDriverWait(self.driver, 15, 0.5).until(EC.presence_of_element_located((By.XPATH, value)))
                 print("找到了")
                 return self.driver.find_element_by_xpath(value)
             except WebDriverException:
                 print("没有找到节点，准备移动")
                 self.movePage(1)
                 return self.driver.find_element_by_xpath(value)
         else:
             print("尝试找css_selector路径路径")
             try:
                 return self.driver.find_element_by_css_selector(value)
             except NoSuchElementException as e:
                 print("没有找到节点，准备移动。错误内容：",e)
                 self.movePage(1)
                 WebDriverWait(self.driver, 15, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR,value)))
                 print("找到了")
                 return self.driver.find_element_by_css_selector(value)
             except WebDriverException as e:
                 print("没有找到节点，准备移动。错误内容：",e)
                 self.movePage(1)
                 return self.driver.find_element_by_css_selector(value)

    # 处理点击找不到的问题
    def handlerClickUnAble(self,elementTarget):
        try:
             elementTarget.click()
        except NoSuchElementException as e:
            print("点击时无法点击，错误信息为：", e)
            time.sleep(2)
            elementTarget.click()
        except WebDriverException as e:
             print("点击时无法点击，错误信息为：",e)
             time.sleep(2)
             elementTarget.click()


    #处理弹框
    def handlerAlert(self,sleepTime=300):
        self.handlerClickUnAble(self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'))
        print("弹框确定")
        self.countAlert+=1
        if self.countAlert>5:
            print("发博太多了，暂停时间：%s秒"%str(sleepTime))
            time.sleep(sleepTime)

        if self.is_element_exist("xpath",'//*[@id="app"]/div[1]/div/header/div[1]'):
            print("尝试关闭")
            self.handlerClickUnAble(self.handlerNoSuchElementException("xpath", '//*[@id="app"]/div[1]/div/header/div[1]'))
            print("关闭评论")

        if self.is_element_exist('css_selector','#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div'):
            print("尝试返回")
            findElement=self.handlerNoSuchElementException('css_selector','#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
            self.handlerClickUnAble(findElement)
            print("已返回")

    #移动鼠标
    def movePage(self,height):
        time.sleep(2)
        if height is None:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif height==1:  # 表示默认移动距离
            self.driver.execute_script("window.scrollTo(0, 50);")
        print("执行了移动鼠标")

    #发表评论
    def writeComment(self,word):
        time.sleep(1)
        self.driver.find_element_by_tag_name("textarea").send_keys(random.choice(word))  # 评论内容
        print("已发表评论")
        self.handlerClickUnAble(self.driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/header/div[3]/a'))   # 发送评论
        print("已发送评论")

    # 搜索关键字
    def searchComment(self):
        try:
            print("开始查找发现按钮")
            WebDriverWait(self.driver, 300, 0.5).until(EC.presence_of_element_located((By.LINK_TEXT, '发现')))
            self.handlerClickUnAble(self.driver.find_element_by_class_name("iconf_navbar_search"))  # 搜索按钮
            self.driver.find_element_by_class_name("forSearch").send_keys(self.findKeyWord + Keys.RETURN)  # 搜索文字
        except NoSuchElementException as e:
            print("searchComment 抛出的异常：",e)
            print("cookies存在，但是过期了")
            self.writeToCookieFile()
        except TimeoutException as e:
            print("searchComment 抛出的异常：",e)
            print("进入到了其他界面")
            self.driver.quit()

    # 热门微博
    def hotWeiBoComment(self):
        self.handlerClickUnAble(self.driver.find_element_by_link_text('发现')) # 发现按钮
        self.handlerClickUnAble(self.driver.find_element_by_css_selector('.card.card4.line-around')) # 热门微博按钮

    # 话题
    def huaTiComment(self):
        self.searchComment()
        self.handlerClickUnAble(self.handlerNoSuchElementException("xpath",'//*[@id="app"]/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div/ul/li[10]'))

    # 休息时间
    def startSleep(self):
        print("开始休息%d秒" % int(self.timeSleep))
        time.sleep(int(self.timeSleep))  # 1分钟运行一次，防止发博太快了
        print("休息结束")

    # 再次查找元素
    def findNodeAgain(self,css,parent=None):
        fromDriver=self.driver
        if parent :
            fromDriver=parent
        WebDriverWait(fromDriver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, css)))
        print("等待节点，并找到了")
        try:
            WebDriverWait(fromDriver, 60, 0.5).until(EC.presence_of_element_located((By.XPATH, css)))
            return fromDriver.find_element_by_xpath(css)
        except StaleElementReferenceException as e:
            print("抛出异常=",e,"重新找节点")
            return fromDriver.find_element_by_xpath(css)

    def realOp(self,startIndex):
        commendlist = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
        print(len(commendlist))
        if len(commendlist) == 0:
            self.movePage(None)
        for i in range(startIndex,len(commendlist)):
            print("-----------------" + str(i) + "-----------------")
            # 避免发博太多导致的限制。
            time.sleep(3)
            # 下面重新获取"转发，评论，赞" 是因为进行下面一系列操作之后，返回到主页面时，内容已经改变，所以需要重新获取
            newcommendlist = self.driver.find_elements_by_css_selector(".m-ctrl-box.m-box-center-a")
            try:
                btnClick = newcommendlist[i].find_elements_by_css_selector(".m-diy-btn.m-box-col.m-box-center.m-box-center-a")[1]
            except IndexError:
                print("越界了，i的值为%d, newCommendlist的长度为%d" % (i, len(newcommendlist)))

            try:
                btnClick.click()  # 外部评论
            except WebDriverException:
                self.movePage(1)
                btnClick.click()

            print("已点击外部评论")
            # 只有小于1条的评论，直接写入评论
            if not self.is_element_exist("xpath",
                                         '// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]'):
                print("处理小于1条评论的情况")
                self.writeComment(self.commentSet)
                # 弹框处理
                if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                    self.handlerAlert()
                    self.startSleep()
                    continue
                self.startSleep()
                continue

            time.sleep(1)
            self.findNodeAgain('// *[ @ id = "app"] / div[1] / div / div[2] / div / div / footer / div[2]').click()
            print("已点击内部评论")
            self.writeComment(self.commentSet)
            # 弹框处理
            if self.is_element_exist("xpath", '//*[@id="app"]/div[2]/div[1]/div[2]/footer/div/a'):
                self.handlerAlert()
                self.startSleep()
                continue

            if self.is_element_exist("xpath", '//*[@id="app"]/div[1]/div/div[1]/div/div[1]/div'):
                backBtn = self.driver.find_element_by_css_selector(
                    '#app > div:nth-child(1) > div > div.m-top-bar.m-panel.m-container-max.m-topbar-max > div > div.nav-left > div')
                self.handlerClickUnAble(backBtn)
                print("已返回")
            self.startSleep()
        return len(commendlist)

    def opNumber(self,startNum):
        print("开始执行第%d次"%(startNum+1))
        return self.realOp(startNum)

    def doOp(self):
        self.driver.get('https://m.weibo.cn/')

        # 删除第一次建立连接时的cookie
        self.driver.delete_all_cookies()
        # 读取登录时存储到本地的cookie
        with open('cookies.json', 'r', encoding='utf-8') as f:
            listCookies = json.loads(f.read())
        for cookie in listCookies:
            self.driver.add_cookie({
                'domain': '.weibo.cn',
                'name': cookie['name'],
                'value': cookie['value'],
                'path': '/',
                'expiry': None
            })
        # 再次访问页面，便可实现免登陆访问
        self.driver.get('https://m.weibo.cn/')
        if  self.commentMode==1:   # 模式1为搜索
            self.searchComment()
        elif self.commentMode==2:  # 模式2为热门
            self.hotWeiBoComment()
        elif self.commentMode==3:   # 模式3为话题
            self.huatiComment()

        lastStartIndex = 0
        for i in range(6):
             lastStartIndex=self.opNumber(lastStartIndex)

        print("------------执行完了，准备关闭------------")
        self.driver.quit()


getUrl = "https://m.weibo.cn/"

commentMode=1
with open('configComment.json', 'r', encoding='utf-8') as f:
    configs = json.loads(f.read())
    for cookie in configs:
        keyWord=cookie["keyWord"]
        commendSet=tuple(cookie['commentSet'])
        timeSleep=cookie["time"]

while True:
    classDriver = weiBoOpClass(webdriver.Chrome())
    try:
        classDriver.startOp(getUrl, keyWord, commendSet,commentMode,timeSleep)
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
    finally:
        timeSleepTime = 10
        print("------------防止发博太快，暂停%d秒----------------" % timeSleepTime)
        time.sleep(timeSleepTime)
        print("重新运行")
        classDriver.driver.quit()
        weiBoOpClass(webdriver.Chrome()).startOp(getUrl, keyWord, commendSet,commentMode,timeSleep)
