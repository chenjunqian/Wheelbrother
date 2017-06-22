#coding=utf-8
import MySQLdb
import jieba
import json
from collections import Counter
import numpy
import math
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class naive_bayesian(object):

    def __init__(self):
        self.connection = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db='mysite',
            charset="utf8"
        )
        self.cursor = self.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def is_chinese(self, string):
        """determine whether the word is Chinese"""
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(string)

        if match:
            return True
        else:
            return False

    def chinese_filter_separator(self, string):
        '''
            过滤掉非中文的文字
        '''
        chinese_word_string = list()
        for word in string:
            if self.is_chinese(word):
                chinese_word_string.append(word)
        return ''.join(chinese_word_string)

    def get_high_frequency_word(self):
        '''
            Get the highest frequency of the word from the database
        '''
        activitiy_query = "SELECT answer_content FROM wheelbrother_voteupanswer"
        self.cursor.execute(activitiy_query)
        activites = self.cursor.fetchall()

        activitiy_query = "SELECT answer_content FROM wheelbrother_collectionanswer"
        self.cursor.execute(activitiy_query)
        voteup_activites = self.cursor.fetchall()
        activites = activites + voteup_activites

        word_list = list()
        chinese_word_string = list()
        activity_string = list()
        for activity in activites:
            activity_string.append(activity['answer_content'])

        for item in ''.join(activity_string):
            if self.is_chinese(item):
                chinese_word_string.append(item)

        seg_list = jieba.cut(''.join(chinese_word_string))

        for item in seg_list:
            if len(item) >= 2:
                word_list.append(item)

        word_count = Counter(word_list)
        json_dict = dict()
        key_word_list = list()
        for item in word_count.most_common(5000):
            # json_dict[item[0]] = item[1]
            key_word_list.append(item[0])

        json_dict['key_word_list'] = key_word_list

        with open("key_word.json", "w") as outfile:
            json.dump(json_dict, outfile, ensure_ascii=False, indent=4)


    def set_of_word_to_vector(self, vocab_list, input_set, is_test_data=False):
        '''
            Create a vector which all the element are 0,
            and change the element to one which contain high frequency word
        '''

        # alignment of data
        return_vector = [0]*500
        if len(input_set) > 500:
            input_set = input_set[:500]

        for word in input_set:
            if word in vocab_list:
                return_vector[input_set.index(word)] += 1
            # else:
            #     print "the word : %s is not in my vocabulary ! " % word

        return return_vector

    def build_data_set(self):
        '''
            load data from database, split words and buil training set
        '''
        activitiy_query = "SELECT answer_content FROM wheelbrother_voteupanswer"
        self.cursor.execute(activitiy_query)
        voteup_activites = self.cursor.fetchall()

        activitiy_query = "SELECT answer_content FROM wheelbrother_collectionanswer"
        self.cursor.execute(activitiy_query)
        collection_activites = self.cursor.fetchall()

        # 0 represent normal activites, and 1 represent target activities
        class_vector = [0]*len(voteup_activites) + [1]*len(collection_activites)

        activities_list = list()
        for item in voteup_activites:
            voteup_activites_chinese_word_string = list()
            for word in item['answer_content']:
                if self.is_chinese(word):
                    voteup_activites_chinese_word_string.append(word)

            seg_list = jieba.cut(''.join(voteup_activites_chinese_word_string))
            item_word_list = list()
            for item in seg_list:
                if len(item) >= 2:
                    item_word_list.append(item)
            activities_list.append(item_word_list)
            print 'cut voteup activity item done !'

        for item in collection_activites:
            collection_activites_chinese_word_string = list()
            for word in item['answer_content']:
                if self.is_chinese(word):
                    collection_activites_chinese_word_string.append(word)

            seg_list = jieba.cut(''.join(collection_activites_chinese_word_string))
            item_word_list = list()
            for item in seg_list:
                if len(item) >= 2:
                    item_word_list.append(item)
            activities_list.append(item_word_list)
            print 'cut collection activity item done !'

        with open('train_set.json', 'w') as json_file:
            json_dict = dict()
            json_dict['train_set'] = activities_list
            json_dict['class_vector'] = class_vector
            json.dump(json_dict, json_file, ensure_ascii=False, indent=4)
        print 'build data set done !'


    def train_naive_bayes(self, train_matrix, key_word_list):
        '''
            Training Naive Bayesian Classifier
        '''
        num_train_docs = len(train_matrix)
        num_words = len(train_matrix[0])
        posibility_of_target = numpy.sum(key_word_list)/numpy.float(num_train_docs)
        #Init possibility
        posibility_zero_num = numpy.ones(num_words)
        posibility_one_num = numpy.ones(num_words)
        posibility_zero_denom = 2.0
        posibility_one_denom = 2.0

        for i in range(num_train_docs):
            if key_word_list[i] == 1:
                posibility_one_num += train_matrix[i]
                posibility_one_denom += numpy.sum(train_matrix[i])
            else:
                posibility_zero_num += train_matrix[i]
                posibility_zero_denom += numpy.sum(train_matrix[i])
        posibility_one_vector = numpy.log10(posibility_one_num/posibility_one_denom)
        posibility_zero_vector = numpy.log10(posibility_zero_num/posibility_one_denom)
        return posibility_zero_vector, posibility_one_vector, posibility_of_target

    def classify_naive_bayes(self, vec_of_classify, p_zero_vector, p_one_vector, p_of_target):
        p_one = numpy.sum(vec_of_classify*p_one_vector) + numpy.log10(p_of_target)
        p_zero = numpy.sum(vec_of_classify*p_zero_vector) + numpy.log10(1.0 - p_of_target)
        # print 'p_one :'+str(p_one)+'  p_zero'+str(p_zero)
        if p_one > p_zero:
            return 1
        else:
            return 0
