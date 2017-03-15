#coding=utf-8

from bayes import naive_bayesian
from crawler import Zhihu
import logging
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    test_training_data = naive_bayesian()
    test_training_data.get_high_frequency_word()
