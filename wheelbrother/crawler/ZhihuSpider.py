#coding=utf-8
"""crawl zhi hu website """
from bs4 import BeautifulSoup

ZHIHU_URL = 'https://www.zhihu.com'
VCZH_URL = ZHIHU_URL + '/people/excited-vczh'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 '+
                  '(X11; Linux x86_64) AppleWebKit/537.36 '+
                  '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/",
    'X-Requested-With': "XMLHttpRequest"
}


class ZhihuActivitiesCrawler(object):
    '''爬取用户动态'''

    def __init__(self, session):
        self.session = session

    def scrawl_activities(self):
        """爬取用户动态入口函数"""
        url = 'https://www.zhihu.com/people/excited-vczh/activities'
        response = self.session.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_divs = soup.find_all('h2', class_='ContentItem-title')
        # print title_divs
        for div in title_divs:
            print div.a.string

        activity_item_meta_title = soup.find_all('span', class_='ActivityItem-metaTitle')

    def get_more_activities(self, after_id):
        '''
            获取更多的用户动态
        '''
        api_url = VCZH_URL + '/activities'
        query_data = {
            'limit':20,
            'after_id':after_id,
            'desktop':True
        }

        response = self.session.post(
            api_url,
            params=query_data,
            headers=HEADERS,
        )

        return response.text
