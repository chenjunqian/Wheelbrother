#coding=utf-8
from session import CrawlerSession
from ZhihuLogin import Login
from ZhihuSpider import ZhihuActivitiesCrawler

try:
    input = raw_input
except:
    pass

if __name__ == '__main__':
    scrawler_session = CrawlerSession()
    zhihu_login = Login(scrawler_session.get_session())
    if zhihu_login.is_login:
        print '已登录 \n'
    else:
        account = input('输入账号 \n > ')
        password = input('输入密码 \n > ')
        zhihu_login.login(account, password)

    if zhihu_login.is_login:
        activities_scrawler = ZhihuActivitiesCrawler(scrawler_session.get_session())
        activities_scrawler.scrawl_activities()
