#coding=utf-8
import cookielib
import requests

class CrawlerSession(object):
    '''初始化全局参数'''
    def __init__(self):
        # 使用登录cookie信息
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookies')
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print "Cookie 未能加载"

    def set_cookies(self, cookies):
        self.session.cookies = cookies

    def get_cookies(self):
        return self.session.cookies

    def set_session(self, session):
        self.session = session

    def get_session(self):
        return self.session
