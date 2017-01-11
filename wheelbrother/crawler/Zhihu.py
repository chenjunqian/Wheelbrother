#coding=utf-8
"""crawl zhi hu website """
import re
import time
import json
import os
from bs4 import BeautifulSoup
from PIL import Image
from wheelbrother.models import VoteupAnswer, VoteupComment, FollowQuestion, AnswerQuestion


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
            #使用线程池爬取用户动态
            for activity in activities:
                self.parse_activitis(activity)

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
            print '\n赞同了回答 \n'
            self.get_voteup_answer_content(activity)

        if activity.attrs['data-type-detail'] == 'member_follow_question':
            #关注了问题
            print '\n 关注了问题 \n'
            self.get_follow_question(activity)

        if activity.attrs['data-type-detail'] == 'member_answer_question':
            #回答了问题
            print '\n回答了问题 \n'
            self.get_member_answer_question(activity)

        if activity.attrs['data-type-detail'] == 'member_follow_column':
            #关注了专栏
            print '\n关注了专栏 \n'

        if activity.attrs['data-type-detail'] == 'member_voteup_article':
            #赞同了文章
            print '\n赞同了文章 \n'

        if activity.attrs['data-type-detail'] == 'member_create_article':
            #发布了文章
            print '\n发布了文章 \n'

    def get_voteup_answer_content(self, activity):
        '''
            解析赞同回答的内容
        '''
        voteupAnswer = VoteupAnswer()
        print '开始获取赞同答案信息 '
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
            user_link = ''
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
                print '已经在数据库中'
                return
        except:
            pass

        voteupAnswer.user_link = ZHIHU_URL.join(user_link)
        voteupAnswer.username = username
        voteupAnswer.answer_id = answer_id
        voteupAnswer.answer_content = answer_content
        voteupAnswer.question_id = question_id
        voteupAnswer.answer_vote_count = answer_vote_count
        voteupAnswer.answer_comment_id = answer_comment_id

        print 'user_link : '+str(user_link)
        print ''.join(username).encode('utf-8').strip()
        print 'answer_id : '+str(answer_id)
        print ''.join(answer_content).encode('utf-8').strip()
        print 'answer_data_time : '+str(answer_data_time)
        print 'answer_vote_count : '+str(answer_vote_count)
        print 'answer_comment_id : '+str(answer_comment_id)
        print 'question_link : '+str(question_link)
        print 'quetion_id : '+str(question_id)

        self.get_comment(answer_comment_id)

    def get_comment(self, answer_comment_id):
        '''
            获取赞同回答的评论
        '''
        current_page = 1
        total_page = 1
        #获取评论url
        MORE_COMMENT_URL = ZHIHU_URL + '/r/answers/'+answer_comment_id+'/comments?page='

        print '开始获取评论信息 '

        comments = self.session.get(MORE_COMMENT_URL+str(current_page), headers=HEADERS)
        comments_json_result = json.loads(comments.text)
        total_count = comments_json_result['paging']['totalCount']
        per_page = comments_json_result['paging']['perPage']
        total_page = (total_count/per_page) + 1

        while current_page <= total_page:
            try:
                comments = self.session.get(MORE_COMMENT_URL+str(current_page), headers=HEADERS)
                comments_json_result = json.loads(comments.text)
                print 'current page number : '+str(current_page)
                if len(comments_json_result['data']) < 1:
                    break

                for comment in comments_json_result['data']:
                    self.parse_comment_result(comment)

                current_page = current_page + 1
                time.sleep(10)
            except:
                break


    def parse_comment_result(self, comment):
        '''
            解析赞同回答的评论
        '''
        voteupComment = VoteupComment()
        try:
            #有匿名的情况
            voteupComment.user_link = comment['author']['url']
            voteupComment.username = comment['author']['name']
            print 'comment user url: '+comment['author']['url']
            print comment['author']['name']
        except:
            voteupComment.user_link = ''
            voteupComment.username = 'anonymous'

        voteupComment.comment_id = comment['id']
        voteupComment.comment_content = comment['content']
        voteupComment.created_time = comment['createdTime']
        voteupComment.like_count = comment['likesCount']
        voteupComment.dislikes_count = comment['dislikesCount']
        voteupComment.in_reply_to_comment_id = comment['inReplyToCommentId']

        print comment['content']
        print 'comment id: '+str(comment['id'])
        print 'comment createdTime: '+str(comment['createdTime'])
        print 'comment inReplyToCommentId: '+str(comment['inReplyToCommentId'])
        print 'comment likesCount: '+str(comment['likesCount'])
        print 'comment dislikesCount: '+str(comment['dislikesCount'])

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
        followQuestion.question_title = question_title

        print 'question_link : '+question_link
        print 'question_id : '+str(question_id)
        print 'question_title : '+question_title


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

        answerQuestion = AnswerQuestion()
        answerQuestion.question_id = question_id
        answerQuestion.question_title = question_title
        answerQuestion.answer_content = answer_content
        answerQuestion.answer_id = answer_id
        answerQuestion.created_time = created_time
        answerQuestion.answer_comment_id = answer_comment_id

        print 'question_id : ' + str(question_id)
        print 'question_link : ' + question_link
        print 'answer_id : ' + str(answer_id)
        print 'answer_comment_id : '+str(answer_comment_id)
        print 'created_time : '+str(created_time)
        print question_title
        print answer_content

        self.get_comment(answer_comment_id)
