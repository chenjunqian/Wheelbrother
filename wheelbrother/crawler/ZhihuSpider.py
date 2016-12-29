#coding=utf-8
"""crawl zhi hu website """
from bs4 import BeautifulSoup

class ZhihuActivitiesCrawler(object):
    '''爬取用户动态'''
    def __init__(self, session):
        self.session = session

    def scrawl_activities(self):
        """爬取用户动态入口函数"""
        url = 'https://www.zhihu.com/people/excited-vczh/activities'
        header = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) '
                         +'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2950.4 Safari/537.36'
        }
        response = self.session.get(url, headers=header)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_divs = soup.find_all('h2', class_='ContentItem-title')
        # print title_divs
        for div in title_divs:
            print div.a.string

        activity_item_meta_title = soup.find_all('span', class_='ActivityItem-metaTitle')

        for span in activity_item_meta_title:
            print span.string
