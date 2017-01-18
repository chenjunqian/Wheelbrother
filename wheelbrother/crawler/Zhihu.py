#coding=utf-8
"""crawl zhi hu website """
import re
import time
import json
import os
import logging
import requests
from bs4 import BeautifulSoup
from PIL import Image
from wheelbrother.models import VoteupAnswer, VoteupComment, FollowQuestion, VoteupArticle, AnswerQuestion


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

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handle = logging.FileHandler('ZhihuCrawl.log')
        handle.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter.converter = time.localtime
        handle.setFormatter(formatter)
        self.logger.addHandler(handle)

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
        start = 1421184149 #获取动态的时间戳 0 则是从现在开始获取

        crawl_times = 0
        response = []

        while limit == 20:
            try:
                response = self.get_more_activities(limit, start)
            except requests.exceptions.ConnectionError:
                self.logger.exception('connection refused')
                print 'Get activities connection refused, waiting for 120s......'
                time.sleep(120)
                continue
            except:
                self.logger.exception('Get activities error')
                print 'Get activities error, waiting for 120s......'
                time.sleep(120)
                continue

            json_response = json.loads(response)
            limit = json_response['msg'][0]
            soup = BeautifulSoup(json_response['msg'][1], 'html.parser')
            activities = soup.find_all('div', class_='zm-profile-section-item zm-item clearfix')
            if len(activities) > 0:
                start = activities[-1]['data-time']

            for activity in activities:
                self.parse_activitis(activity)

            crawl_times = crawl_times + 1
            if crawl_times == 10:
                self.logger.info('crawl activities 10 times, sleep 60s...')
                time.sleep(60)
            elif crawl_times == 20:
                self.logger.info('crawl activities 20 times, sleep 80s...')
                time.sleep(80)
            elif crawl_times == 30:
                self.logger.info('crawl activities 30 times, sleep 1200s...')
                crawl_times = 0
                time.sleep(1200)
            else:
                self.logger.info('crawl activities, waiting for 20s...')
                time.sleep(20)

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

    def parse_activitis(self, activity):
        '''根据不同的标签来判断用户动态的类型'''
        if activity.attrs['data-type-detail'] == 'member_voteup_answer':
            #赞同了回答
            self.logger.info('\n赞同了回答 \n')
            self.get_voteup_answer_content(activity)

        if activity.attrs['data-type-detail'] == 'member_follow_question':
            #关注了问题
            self.logger.info('\n 关注了问题 \n')
            self.get_follow_question(activity)

        if activity.attrs['data-type-detail'] == 'member_answer_question':
            #回答了问题
            self.logger.info('\n回答了问题 \n')
            self.get_member_answer_question(activity)

        if activity.attrs['data-type-detail'] == 'member_follow_column':
            #关注了专栏
            self.logger.info('\n关注了专栏 \n')

        if activity.attrs['data-type-detail'] == 'member_voteup_article':
            #赞同了文章
            self.logger.info('\n赞同了文章 \n')
            self.get_member_voteup_article(activity)

        if activity.attrs['data-type-detail'] == 'member_create_article':
            #发布了文章
            self.logger.info('\n发布了文章 \n')

    def get_voteup_answer_content(self, activity):
        '''
            解析赞同回答的内容
        '''
        voteupAnswer = VoteupAnswer()
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

        try:
            #判断是否在数据库中已经存在
            check_model = VoteupAnswer.objects.get(answer_id=answer_id)
            if check_model:
                self.logger.info('赞同的答案已经在数据库中')
                return
        except:
            pass

        voteupAnswer.user_link = ZHIHU_URL.join(user_link)
        voteupAnswer.username = ''.join(username).encode('utf-8').strip()
        voteupAnswer.answer_id = answer_id
        voteupAnswer.answer_content = ''.join(answer_content).encode('utf-8').strip()
        voteupAnswer.question_id = question_id
        voteupAnswer.answer_vote_count = answer_vote_count
        voteupAnswer.answer_comment_id = answer_comment_id
        voteupAnswer.answer_data_time = answer_data_time
        voteupAnswer.save()
        self.logger.info('save voteup answer successful '+
                         ''.join(answer_content).encode('utf-8').strip()+'\n'+
                         'time : '+str(answer_data_time))

        self.get_comment(answer_comment_id)

    def get_comment(self, answer_comment_id):
        '''
            获取赞同回答的评论
        '''
        current_page = 1
        #获取评论url
        MORE_COMMENT_URL = ZHIHU_URL + '/r/answers/'+answer_comment_id+'/comments?page='

        comments = []

        try:
            #只获取一页的评论,同时赞数最多的评论就在第一页
            comments = self.session.get(
                MORE_COMMENT_URL+str(current_page),
                headers=HEADERS,
                verify=False
                )
        except requests.exceptions.ConnectionError:
            self.logger.exception('Get comment connection refused')
            time.sleep(40)
            self.get_comment(answer_comment_id)
        except:
            self.logger.exception('Get comment error')
            time.sleep(40)
            return

        comments_json_result = json.loads(comments.text)
        if len(comments_json_result['data']) < 1:
            return

        for comment in comments_json_result['data']:
            if self.parse_comment_result(comment) is None:
                break

        self.logger.info('waiting for 20s......')
        time.sleep(20)

    def parse_comment_result(self, comment):
        '''
            解析赞同回答的评论
        '''

        try:
            #判断是否在数据库中已经存在
            check_model = VoteupAnswer.objects.get(comment_id=comment['id'])
            if check_model:
                self.logger.info('评论已经在数据库中')
                return
        except:
            pass

        voteupComment = VoteupComment()
        try:
            #有匿名的情况
            voteupComment.user_link = comment['author']['url']
            voteupComment.username = comment['author']['name']
        except:
            voteupComment.user_link = ZHIHU_URL
            voteupComment.username = 'anonymous'

        voteupComment.comment_id = comment['id']
        voteupComment.comment_content = ''.join(comment['content']).encode('utf-8').strip()
        voteupComment.created_time = comment['createdTime']
        voteupComment.like_count = comment['likesCount']
        voteupComment.dislikes_count = comment['dislikesCount']
        voteupComment.in_reply_to_comment_id = comment['inReplyToCommentId']
        voteupComment.save()
        self.logger.info('save voteup comment '+
                         ''.join(comment['content']).encode('utf-8').strip()+'/n'+
                         'time : '+str(comment['createdTime']))
        return voteupComment

    def get_follow_question(self, activity):
        '''
            解析关注问题的信息
        '''
        question_link = activity.find('a', class_='question_link').get('href')
        question_id = re.findall(r"(?<=/question/).*", question_link)[0]
        question_title = activity.find('a', class_='question_link').string

        followQuestion = FollowQuestion()
        followQuestion.question_id = question_id
        followQuestion.question_link = question_link
        followQuestion.question_title = ''.join(question_title).encode('utf-8').strip()
        followQuestion.save()
        self.logger.info('save follow question '+
                         ''.join(question_title).encode('utf-8').strip())

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

        try:
            #判断是否在数据库中已经存在
            check_model = AnswerQuestion.objects.get(answer_id=answer_id)
            if check_model:
                self.logger.info('回答的问题已经在数据库中\n')
                return
        except:
            pass

        answerQuestion = AnswerQuestion()
        answerQuestion.question_id = question_id
        answerQuestion.question_title = ''.join(question_title).encode('utf-8').strip()
        answerQuestion.answer_content = ''.join(answer_content).encode('utf-8').strip()
        answerQuestion.answer_id = answer_id
        answerQuestion.created_time = created_time
        answerQuestion.answer_comment_id = answer_comment_id
        answerQuestion.save()
        self.logger.info('save answer question '+
                         ''.join(question_title).encode('utf-8').strip()+' \n'+
                         'time : '+str(created_time))

        self.get_comment(answer_comment_id)

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

        try:
            #判断是否在数据库中已经存在
            check_model = VoteupArticle.objects.get(article_url_token=article_url_token)
            if check_model:
                self.logger.info('赞同的文章已经在数据库中 \n')
                return
        except:
            pass

        voteupArticle = VoteupArticle()
        voteupArticle.user_link = ZHIHU_URL+user_link
        voteupArticle.article_title = ''.join(article_title).encode('utf-8').strip()
        voteupArticle.article_url_token = article_url_token
        voteupArticle.article_id = article_id
        voteupArticle.article_content = ''.join(article_content).encode('utf-8').strip()
        voteupArticle.created_time = created_time
        voteupArticle.save()
        self.logger.info('save voteup article '+
                         ''.join(article_title).encode('utf-8').strip()+' \n'+
                         'time : '+str(created_time))
