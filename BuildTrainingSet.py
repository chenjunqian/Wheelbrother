#coding=utf-8
import MySQLdb
import jieba
from collections import Counter
import re
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class TrainingData(object):

    def __init__(self):
        self.connection = MySQLdb.connect(
            host='42.96.208.219',
            port=3306,
            user='root',
            passwd='root',
            db='mysite',
            charset="utf8"
        )
        self.cursor = self.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def is_chinese(self, string):
        """判断一个unicode是否是汉字"""
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(string)

        if match:
            return True
        else:
            return False


    def get_high_frequency_word(self):
        '''Get the highest frequency of the word from the database '''
        activites = {}
        activitiy_query = "SELECT * FROM wheelbrother_voteupanswer ORDER BY id DESC LIMIT %s,%s"
        query_value = [0, 500]
        self.cursor.execute(activitiy_query, query_value)
        activites = self.cursor.fetchall()

        # target_index = 100
        word_list = list()
        chinese_word_string = str()
        activity_string = str()
        for activity in activites:
            activity_string = activity_string+activity['answer_content']

        for item in activity_string:
            if self.is_chinese(item):
                chinese_word_string = chinese_word_string+item

        seg_list = jieba.cut(chinese_word_string)

        for item in seg_list:
            if len(item) >= 2:
                word_list.append(item)

        word_count = Counter(word_list)
        for item in word_count.most_common(500):
            print item[0]+' : '+str(item[1])
