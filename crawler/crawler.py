#coding=utf-8
import time
import json
import Zhihu
from session import CrawlerSession
from getpass import getpass
import logging
import MySQLdb
import requests
from bs4 import BeautifulSoup

class zhihu_crawler:

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handle = logging.FileHandler('ZhihuCrawl.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter.converter = time.localtime
        handle.setFormatter(formatter)
        self.logger.addHandler(handle)

        self.connection = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='root',
            db='mysite',
        )
        self.cursor = self.connection.cursor()


    def run(self):
        try:
            input = raw_input
        except:
            pass

        crawler_session = CrawlerSession()
        zhihu_client = Zhihu.ZhihuClient(crawler_session.get_session(), self.logger)
        if zhihu_client.is_login:
            print '已登录 \n'
        else:
            account = input('输入账号 \n > ')
            password = getpass("请输入登录密码: ")
            zhihu_client.login(account, password)

        if zhihu_client.is_login:
            self.crawl_activities(zhihu_client)


        #####爬取用户动态#######
    def crawl_activities(self, zhihu_client):
        """爬取用户动态入口函数"""
        limit = 20
        start = 0 #获取动态的时间戳 0 则是从现在开始获取

        crawl_times = 0
        response = []

        while True:
            try:
                response = zhihu_client.get_more_activities(limit, start)
                print response
                json_response = json.loads(response)
            except requests.exceptions.ConnectionError:
                self.logger.exception('connection refused')
                print 'Catch activities connection refused, waiting for 120s......'
                time.sleep(120)
                continue
            except ValueError:
                self.logger.exception('Catch activities ValueError'+
                                      ' maybe No JSON object could be decoded')
                print 'Get activities error, waiting for 1200s, and then break......'
                time.sleep(1200)
                break
            except:
                self.logger.exception('Catch activities error')
                print 'Get activities error, waiting for 1200s, and then break......'
                time.sleep(1200)
                break

            limit = json_response['msg'][0]
            soup = BeautifulSoup(json_response['msg'][1], 'html.parser')
            activities = soup.find_all('div', class_='zm-profile-section-item zm-item clearfix')
            if len(activities) > 0:
                start = activities[-1]['data-time']
                self.logger.info('start time : '+str(start))

            for activity in activities:
                self.parse_activitis(zhihu_client, activity)

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

    def parse_activitis(self, zhihu_client, activity):
        '''根据不同的标签来判断用户动态的类型'''
        if activity.attrs['data-type-detail'] == 'member_voteup_answer':
            #赞同了回答
            self.logger.info('\n赞同了回答 \n')
            question_content = zhihu_client.get_voteup_answer_content(activity)

            try:
                #判断是否在数据库中已经存在
                check_query = "SELECT * FROM wheelbrother_voteupanswer WHERE answer_id=%s"
                self.cursor.execute(check_query, [question_content['answer_id']])
                check_model = self.cursor.fechall()
                if check_model:
                    self.logger.info('赞同的答案已经在数据库中')
                    return
            except:
                pass

            voteup_answer_query = ("INSERT INTO wheelbrother_voteupanswer"+
                                   "(user_link,"+
                                   "username,"+
                                   "answer_id,"+
                                   "answer_content,"+
                                   "question_id,"+
                                   "answer_vote_count,"+
                                   "answer_comment_id,"+
                                   "answer_data_time)"+
                                   " VALUES(%s,%s,%s,%s,%s,%s,%s,%s)")
            self.cursor.execute(
                voteup_answer_query,
                [
                    question_content['user_link'],
                    question_content['username'],
                    question_content['answer_id'],
                    question_content['answer_content'],
                    question_content['question_id'],
                    question_content['answer_vote_count'],
                    question_content['answer_comment_id'],
                    question_content['answer_data_time'],
                ]
            )
            self.logger.info('save voteup answer successful '+
                             question_content['answer_content']+'\n'+
                             'time : '+str(question_content['answer_data_time']))

            comments_json_result = zhihu_client.get_comment(question_content['answer_comment_id'])

            if comments_json_result is None:
                return

            for comment in comments_json_result['data']:
                if self.parse_comment_result(comment) is None:
                    break

            self.logger.info('waiting for 20s......')
            time.sleep(20)

        if activity.attrs['data-type-detail'] == 'member_follow_question':
            #关注了问题
            self.logger.info('\n 关注了问题 \n')
            follow_question_content = zhihu_client.get_follow_question(activity)

            query_value = [
                follow_question_content['question_id'],
                follow_question_content['question_link'],
                follow_question_content['question_title']
            ]


            follow_question_query = (
                "INSERT INTO wheelbrother_followquestion"+
                "(question_id,"+
                "question_link,"+
                "question_title)"
                " VALUES(%s,%s,%s)"
            )

            self.cursor.execute(
                follow_question_query,
                query_value
            )

            self.logger.info('save follow question '+
                             follow_question_content['question_title'])

        if activity.attrs['data-type-detail'] == 'member_answer_question':
            #回答了问题
            self.logger.info('\n回答了问题 \n')
            answer_question_content = zhihu_client.get_member_answer_question(activity)
            try:
                #判断是否在数据库中已经存在
                check_query = "SELECT * FROM wheelbrother_answerquestion WHERE answer_id=%s"
                self.cursor.execute(check_query, [answer_question_content['answer_id']])
                check_model = self.cursor.fechall()
                if check_model:
                    self.logger.info('回答的问题已经在数据库中\n')
                    return
            except:
                pass

            answer_question_query = (
                "INSERT INTO wheelbrother_answerquestion"+
                "(question_id,"+
                "question_title,"+
                "answer_content,"+
                "answer_id,"+
                "created_time,"+
                "answer_comment_id)"
                " VALUES(%s,%s,%s,%s,%s,%s)"
            )

            query_value = [
                answer_question_content['question_id'],
                answer_question_content['question_title'],
                answer_question_content['answer_content'],
                answer_question_content['answer_id'],
                answer_question_content['created_time'],
                answer_question_content['answer_comment_id']
            ]

            self.cursor.execute(
                answer_question_query,
                query_value
            )

            self.logger.info('save answer question '+
                             answer_question_content['question_title']+' \n'+
                             'time : '+str(answer_question_content['created_time']))

            comments_json_result = zhihu_client.get_comment(
                answer_question_content['answer_comment_id']
            )

            if comments_json_result is None:
                return

            for comment in comments_json_result['data']:
                if self.parse_comment_result(comment) is None:
                    break

        if activity.attrs['data-type-detail'] == 'member_follow_column':
            #关注了专栏
            zhihu_client.logger.info('\n关注了专栏 \n')

        if activity.attrs['data-type-detail'] == 'member_voteup_article':
            #赞同了文章
            self.logger.info('\n赞同了文章 \n')
            voteup_article_content = zhihu_client.get_member_voteup_article(activity)

            try:
                #判断是否在数据库中已经存在
                check_query = "SELECT * FROM wheelbrother_voteuparticle WHERE article_url_token=%s"
                self.cursor.execute(check_query, [voteup_article_content['article_url_token']])
                check_model = self.cursor.fechall()
                if check_model:
                    self.logger.info('赞同的文章已经在数据库中 \n')
                    return
            except:
                pass


            voteup_article_query = (
                "INSERT INTO wheelbrother_voteuparticle"+
                "(user_link,"+
                "article_title,"+
                "article_url_token,"+
                "article_id,"+
                "article_content,"+
                "created_time)"
                " VALUES(%s,%s,%s,%s,%s,%s)"
            )

            query_value = [
                voteup_article_content['user_link'],
                voteup_article_content['article_title'],
                voteup_article_content['article_url_token'],
                voteup_article_content['article_id'],
                voteup_article_content['article_content'],
                voteup_article_content['created_time'],
            ]

            self.cursor.execute(
                voteup_article_query,
                query_value
            )

            self.logger.info('save voteup article '+
                             voteup_article_content['article_title']+' \n'+
                             'time : '+str(voteup_article_content['created_time']))

        if activity.attrs['data-type-detail'] == 'member_create_article':
            #发布了文章
            self.logger.info('\n发布了文章 \n')


    def parse_comment_result(self, comment):
        '''
            解析赞同回答的评论
        '''

        try:
            #判断是否在数据库中已经存在
            check_query = "SELECT * FROM wheelbrother_voteupcomment WHERE comment_id=%s"
            self.cursor.execute(check_query, [comment['id']])
            check_model = self.cursor.fechall()
            if check_model:
                self.logger.info('评论已经在数据库中')
                return
        except:
            pass

        try:
            #有匿名的情况
            user_link = comment['author']['url']
            username = comment['author']['name']
        except:
            user_link = Zhihu.ZHIHU_URL
            username = 'anonymous'

        voteup_comment_query = ("INSERT INTO wheelbrother_voteupcomment"+
                                "(comment_id,"+
                                "comment_content,"+
                                "created_time,"+
                                "like_count,"+
                                "dislikes_count,"+
                                "in_reply_to_comment_id,"+
                                "user_link,"+
                                "username)"
                                " VALUES(%s,%s,%s,%s,%s,%s,%s,%s)")
        query_value = [
            comment['id'],
            ''.join(comment['content']).encode('utf-8').strip(),
            comment['createdTime'],
            comment['likesCount'],
            comment['dislikesCount'],
            comment['inReplyToCommentId'],
            user_link,
            ''.join(username).encode('utf-8').strip(),
        ]
        self.cursor.execute(
            voteup_comment_query,
            query_value
        )

        self.logger.info('save voteup comment '+
                         ''.join(comment['content']).encode('utf-8').strip()+'/n'+
                         'time : '+str(comment['createdTime']))
        return query_value

if __name__ == "__main__":
    my_zhihu_crawler = zhihu_crawler(CrawlerSession())
    while True:
        my_zhihu_crawler.run()
        time.sleep(1200)
