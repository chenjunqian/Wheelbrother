#coding=utf-8

from bayes import naive_bayesian
from crawler.crawler import zhihu_crawler
import logging
import pickle
import json
from bs4 import BeautifulSoup
import sys
import MySQLdb
import numpy

reload(sys)
sys.setdefaultencoding('utf-8')

def test_navie_bayes():
    bayes_engine = naive_bayesian()
    zhi_hu_crawler = zhihu_crawler()
    # test_training_data.get_high_frequency_word()
    # test_training_data.build_data_set()
    train_set_dict = dict()
    key_word_set_dict = dict()
    vector_set = list()
    with open('train_set.json', 'r') as json_file:
        train_set_dict = json.load(json_file)

    with open('key_word.json', 'r') as json_file:
        key_word_set_dict = json.load(json_file)

    for item in train_set_dict['train_set']:
        vector_set.append(
            bayes_engine.set_of_word_to_vector(
                key_word_set_dict['key_word_list'],
                item,
                True
            )
        )
    p0v, p1v, pAb = bayes_engine.train_naive_bayes(
        vector_set,
        train_set_dict['class_vector']
    )

    connection = MySQLdb.connect(
        host='118.190.103.54',
        user='root',
        passwd='root',
        db='mysite',
        charset="utf8"
    )
    cursor = connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    feed_query = "SELECT answer_content, answer_id, question_title FROM wheelbrother_feed_voteupanswer ORDER BY id"
    cursor.execute(feed_query)
    feed_result = cursor.fetchall()

    for item in feed_result:
        item['answer_content'] = bayes_engine.chinese_filter_separator(item['answer_content'])
        item_vec = numpy.array(
            bayes_engine.set_of_word_to_vector(
                key_word_set_dict['key_word_list'],
                item['answer_content']
            )
        )
        print item_vec
        result = bayes_engine.classify_naive_bayes(
            item_vec,
            p0v,
            p1v,
            pAb
        )

        if result == 1:
            zhi_hu_crawler.voteup_activities(zhi_hu_crawler.zhihu_client, item['answer_id'])
            print str(item['answer_id'])+' '+str(
                item['question_title']
                )+' classified as '+str(1)

def get_my_activities():
    pass

if __name__ == '__main__':
    test_navie_bayes()
