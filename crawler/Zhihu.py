#coding=utf-8
""" zhihu website crawler API """
import re
import time
import json
import os
import requests
from PIL import Image


ZHIHU_URL = 'https://www.zhihu.com'
VCZH_URL = ZHIHU_URL + '/people/excited-vczh'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 '+
                  '(Linux; Android 6.0; Nexus 5 Build/MRA58N)'+
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'+
                  ' Chrome/57.0.2950.4 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/",
    'X-Requested-With': "XMLHttpRequest"
}


class ZhihuClient(object):
    '''知乎爬虫接口'''

    def __init__(self, session, logger=None):
        self.session = session
        if logger:
            self.logger = logger

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
            print '请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg')
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
            verify=False
        )

        return response.text

    def get_voteup_answer_content(self, activity):
        '''
            解析赞同回答的内容
        '''
        #回答者的用户信息
        author_link_top = activity.find_all('span', class_='summary-wrapper')
        try:
            author_link = author_link_top[0].find('a', class_='author-link')
            user_link = author_link.get('href')
            username = author_link.get_text()
        except:
            '''
            可能会造成的异常为Nonetype, 和IndexError，还不知道为什么会出现有的答案的html结构会不一样
            '''
            user_link = ZHIHU_URL
            username = 'anonymous'

        #答案的信息
        answer_div = activity.find_all('div', class_='zm-item-answer ')
        answer_id = answer_div[0].get('data-atoken')
        answer_data_time = answer_div[0].get('data-created')
        answer_comment_id = answer_div[0].get('data-aid')
        answer_content = answer_div[0].find('textarea', class_='content').string
        answer_vote_count = answer_div[0].find('a', class_='meta-item'+
                                               ' votenum-mobile zm-item-vote-count'+
                                               ' js-openVoteDialog').find('span').string

        #问题的信息
        question_link_a = activity.find_all('a', class_='question_link')
        question_link = question_link_a[0]['href']
        pattern = r'(?<=question/).*?(?=/answer)'
        question_id = re.findall(pattern, question_link)[0]

        question_content = {
            'user_link':user_link,
            'username':username,
            'answer_id':answer_id,
            'answer_content':answer_content,
            'question_id':question_id,
            'answer_vote_count':answer_vote_count,
            'answer_comment_id':answer_comment_id,
            'answer_data_time':answer_data_time
        }

        return question_content

    def get_comment(self, answer_comment_id):
        '''
            获取赞同回答的评论
        '''
        current_page = 1
        #获取评论url
        MORE_COMMENT_URL = ZHIHU_URL + '/r/answers/'+answer_comment_id+'/comments?page='

        try:
            #只获取一页的评论,同时赞数最多的评论就在第一页
            comments = self.session.get(
                MORE_COMMENT_URL+str(current_page),
                headers=HEADERS,
                verify=False
                )
        except requests.exceptions.ConnectionError:
            if self.logger:
                self.logger.exception('Get comment connection refused')
            time.sleep(40)
            return
        except:
            if self.logger:
                self.logger.exception('Get comment error')
            time.sleep(40)
            return

        try:
            comments_json_result = json.loads(comments.text)
            if len(comments_json_result['data']) < 1:
                return

            return comments_json_result
        except ValueError:
            if self.logger:
                self.logger.exception('Myabe No JSON object could be decoded')
            return



    def get_follow_question(self, activity):
        '''
            解析关注问题的信息
        '''
        question_link = activity.find('a', class_='question_link').get('href')
        question_id = re.findall(r"(?<=/question/).*", question_link)[0]
        question_title = activity.find('a', class_='question_link').string

        follow_question_content = {
            'question_link':question_link,
            'question_id':question_id,
            'question_title':question_title,
        }

        return follow_question_content

    def get_member_answer_question(self, activity):
        '''
            解析回答问题的信息
        '''
        question_link = activity.find('a', class_='question_link').get('href')
        question_id = re.findall(r'(?<=question/).*?(?=/answer)', question_link)[0]
        question_title = activity.find('a', class_='question_link').string
        answer_content = activity.find('textarea', class_='content').string
        answer_id = activity.find('div', class_='zm-item-answer ').get('data-atoken')
        answer_comment_id = activity.find('div', class_='zm-item-answer ').get('data-aid')
        created_time = activity.find('div', class_='zm-item-answer ').get('data-created')

        answer_question_content = {
            'question_id':question_id,
            'question_title':question_title,
            'answer_content':answer_content,
            'answer_id':answer_id,
            'created_time':created_time,
            'answer_comment_id':answer_comment_id
        }

        return answer_question_content

    def get_member_voteup_article(self, activity):
        '''
            解析赞同文章的信息
        '''
        try:
            user_link = activity.find(
                'div',
                class_='author-info summary-wrapper'
                ).find('a').get('href')
        except:
            user_link = ''

        article_title = activity.find('a', class_='post-link').string

        article_info_div = activity.find('div', class_='zm-item-feed zm-item-post')
        article_info_div_meta = article_info_div.find_all('meta')

        article_url_token = article_info_div_meta[0].get('content')
        article_id = article_info_div_meta[1].get('content')
        article_content = activity.find('textarea', class_='content').string
        created_time = activity.get('data-time')

        voteup_article_content = {
            'user_link':ZHIHU_URL+user_link,
            'article_title':article_title,
            'article_url_token':article_url_token,
            'article_id':article_id,
            'article_content':article_content,
            'created_time':created_time
        }

        return voteup_article_content

    def get_collection_activites(self, collection_id, page_num):
        '''
            获取收藏夹的内容
        '''
        collection_url = ZHIHU_URL + '/collection/'+str(collection_id)+'/?page='+str(page_num)
        response = self.session.get(
            collection_url,
            headers=HEADERS,
            verify=False
        )

        return response.text

    def parse_collection_activites_content(self, content):
        '''
            解析收藏夹的内容
        '''
        activities_result_set = list()
        activites = content.find_all('div', class_='zm-item')
        for activity in activites:
            activity_result_set = {}
            answer_title = activity.find('h2', class_='zm-item-title').find('a').string
            question_link = activity.find('h2', class_='zm-item-title').find('a').get('href')
            try:
                author_name = activity.find('a', class_='author-link').string
                author_link = activity.find('a', class_='author-link').get('href')
            except AttributeError:
                author_name = 'anonymity'
                author_link = ZHIHU_URL

            answer_content = activity.find('textarea', class_='content').string
            try:
                answer_comment_id = activity.find('div', class_='zm-item-answer').get('data-aid')
                answer_id = activity.find('div', class_='zm-item-answer').get('data-atoken')
            except AttributeError:
                answer_comment_id = '0'
                answer_id = '0'

            activity_result_set['answer_title'] = answer_title
            activity_result_set['question_link'] = question_link
            activity_result_set['author_name'] = author_name
            activity_result_set['author_link'] = author_link
            activity_result_set['answer_content'] = answer_content
            activity_result_set['answer_comment_id'] = answer_comment_id
            activity_result_set['answer_id'] = answer_id
            activities_result_set.append(activity_result_set)

        return activities_result_set
