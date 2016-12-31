#coding=utf-8
from session import CrawlerSession
from Zhihu import ZhihuClient
import time
from getpass import getpass

try:
    input = raw_input
except:
    pass

if __name__ == '__main__':
    crawler_session = CrawlerSession()
    zhihu_client = ZhihuClient(crawler_session.get_session())
    if zhihu_client.is_login:
        print '已登录 \n'
    else:
        account = input('输入账号 \n > ')
        password = getpass("请输入登录密码: ")
        zhihu_client.login(account, password)

    if zhihu_client.is_login:
        zhihu_client.crawl_activities()
