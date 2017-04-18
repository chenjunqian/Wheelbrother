#coding=utf-8

from bayes import naive_bayesian
from crawler import Zhihu
import logging
import pickle
import json
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def test_navie_bayes():
    test_training_data = naive_bayesian()
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
            test_training_data.set_of_word_to_vector(
                key_word_set_dict['key_word_list'],
                item
            )
        )
    p0v, p1v, pAb = test_training_data.train_naive_bayes(
        vector_set,
        train_set_dict['class_vector']
    )
    print 'p0v : '+ str(p0v)
    print 'p1v : '+ str(p1v)
    print 'pAb : '+ str(pAb)

def get_my_activities():
    pass

if __name__ == '__main__':
    pass
