import time

import wx
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import NoSuchElementException

from weiBoOp import weiBoOpClass


class Frame1(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title='坤坤',size=(500,650))
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # 单选按钮
        lblList = ['搜索关键字下评论', '话题下评论']
        self.rbox = wx.RadioBox(self.panel, label='选择在哪评论', pos=(10, 20), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)
        # 1为响应容器改变大小，expand占据窗口的整个宽度
        sizer.Add(self.rbox, 1, wx.ALIGN_TOP | wx.EXPAND)

        # 搜索介绍
        self.keyWordText=wx.StaticText(self.panel, -1, "搜索关键字或者话题关键字",pos=(10, 140))
        # font = wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        # self.keyWordText.SetFont(font)
        self.keyWord = wx.TextCtrl(self.panel,pos=(200, 135),size=(200,25))

        # 评论内容
        self.commentText = wx.StaticText(self.panel, -1, "评论的内容，最多6行，以行分隔", pos=(10, 250))
        self.comment = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        sizer.Add(self.comment, 1, wx.ALIGN_TOP | wx.EXPAND)

        # 开始按钮
        self.button = wx.Button(self.panel, label='开始',pos=(200,200))
        self.Bind(wx.EVT_BUTTON, self.onClick, self.button)
        sizer.Add(self.button,0,wx.EXPAND)

        self.panel.SetSizerAndFit(sizer)
        self.panel.Layout()

    def onClick(self, event):
        print(self.comment.GetValue())
        print("2223")
        keyWord = "范冰冰"
        getUrl = "https://m.weibo.cn/"
        commendSet = ("嗯", "嗯嗯", "唔", "唔唔", "嗯嗯嗯",)

        # while True:
        classDriver = weiBoOpClass(webdriver.Chrome())
        try:
            classDriver.startOp(getUrl, keyWord, commendSet)
            print("222323123123")
        except StaleElementReferenceException as e:
            print("异常", e)
            print("没有加载到节点")
        except NoSuchElementException as e:
            print("异常", e)
            print("没有找到节点")
        except WebDriverException as e:
            print("异常", e)
            print("没有找到位置")
        except ConnectionAbortedError as e:
            print("异常", e)
        finally:
            timeSleepTime = 60
            print("------------防止发博太快，暂停%d秒----------------" % timeSleepTime)
            time.sleep(timeSleepTime)
            print("重新运行")
            classDriver.driver.quit()
            weiBoOpClass(webdriver.Chrome()).startOp(getUrl, keyWord, commendSet)

    def onRadioBox(self, e):
        print(self.rbox.GetSelection())

if __name__ == '__main__':
    app = wx.App()
    frame = Frame1(None)
    frame.Show()
    app.MainLoop()
