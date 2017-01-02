#coding=utf-8
"""crawl zhi hu website """
import re
import time
import json
import os
from bs4 import BeautifulSoup
from PIL import Image
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from wheelbrother.models import VoteupAnswer



ZHIHU_URL = 'https://www.zhihu.com'
VCZH_URL = ZHIHU_URL + '/people/excited-vczh'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 '+
                  '(Linux; Android 6.0; Nexus 5 Build/MRA58N)'+
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'+
                  ' Chrome/57.0.2950.4 Mobile Safari/537.36',
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/",
    'X-Requested-With': "XMLHttpRequest"
}


class ZhihuClient(object):
    '''知乎爬虫接口'''

    def __init__(self, session):
        self.session = session

    def login(self, account, password):
        """登录知乎"""
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf':self.get_xsrf(),
            'password':password,
            'remember_me': 'true',
            'email': account,
        }

        try:
            login_page = self.session.post(post_url, data=post_data, headers=HEADERS)
            login_code = login_page.text
            print login_page.status_code
            print login_code
        except:
            # 需要输入验证码后才能登录成功
            postdata = {}
            postdata["captcha"] = self.get_captcha()
            login_page = self.session.post(post_url, data=postdata, headers=HEADERS)
            login_code = eval(login_page.text)
            print login_code['msg']

        self.session.cookies.save()

    def is_login(self):
        '''通过查看用户个人信息来判断是否已经登录'''
        url = "https://www.zhihu.com/settings/profile"
        login_code = self.session.get(url, headers=HEADERS, allow_redirects=False).status_code
        if login_code == 200:
            return True
        else:
            return False


    def get_captcha(self):
        ''' 获取验证码'''
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.session.get(captcha_url, headers=HEADERS)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print (u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha\n>")
        return captcha


    def get_xsrf(self):
        '''_xsrf 是一个动态变化的参数'''
        index_url = 'https://www.zhihu.com'
        # 获取登录时需要用到的_xsrf
        index_page = self.session.get(index_url, headers=HEADERS)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 这里的_xsrf 返回的是一个list
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]



    #####爬取用户动态#######

    def crawl_activities(self):
        """爬取用户动态入口函数"""
        limit = 20
        start = '0'

        while limit == 20:
            response = self.get_more_activities(limit, start)
            json_response = json.loads(response)
            limit = json_response['msg'][0]
            soup = BeautifulSoup(json_response['msg'][1], 'html.parser')
            activities = soup.find_all('div', class_='zm-profile-section-item zm-item clearfix')
            start = activities[-1]['data-time'] if len(json_response) > 0 else 0
            for activity in activities:
                if activity.attrs['data-type-detail'] == 'member_voteup_answer':
                    #赞同了回答
                    print '赞同了回答'
                    self.get_voteup_answer_content(activity)
                    continue
                if activity.attrs['data-type-detail'] == 'member_follow_question':
                    #关注了问题
                    print '关注了问题'
                    continue
                if activity.attrs['data-type-detail'] == 'member_follow_column':
                    #关注了专栏
                    print '关注了专栏'
                    continue
                if activity.attrs['data-type-detail'] == 'member_voteup_article':
                    #赞同了文章
                    print '赞同了文章'
                    continue
                if activity.attrs['data-type-detail'] == 'member_create_article':
                    #发布了文章
                    print '发布了文章'
                    continue
                if activity.attrs['data-type-detail'] == 'member_answer_question':
                    #回答了问题
                    print '回答了问题'
                    continue

    def get_more_activities(self, limit, start):
        '''
            获取更多的用户动态
        '''
        api_url = VCZH_URL + '/activities'
        query_data = {
            'limit':limit,
            'start':start,
        }

        response = self.session.post(
            api_url,
            params=query_data,
            headers=HEADERS,
        )

        return response.text

    def get_voteup_answer_content(self, activity):
        '''
            解析赞同回答的内容
        '''
        voteupAnswer = VoteupAnswer()

        author_link_top = activity.find_all('span', class_='summary-wrapper')

        try:
            author_link = author_link_top[0].find('a', class_='author-link')
            user_link = author_link.get('href')
            username = author_link.get_text()
        except:
            '''
            可能会造成的异常为Nonetype, 和IndexError
            '''
            user_link = ''
            username = 'anonymous'

        answer_div = activity.find_all('div', class_='zm-item-answer ')
        answer_id = answer_div[0].get('data-atoken')

        print 'user_link : '+str(user_link)
        print username
        print 'answer_id : '+str(answer_id)

        voteupAnswer.user_link = user_link
        voteupAnswer.username = username
        voteupAnswer.answer_id = answer_id

    def get_voteup_comment(self):
        '''
            解析赞同回答的评论
        '''
        pass
