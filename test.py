#coding=utf-8

from BuildTrainingSet import TrainingData
from crawler import Zhihu
import logging
from crawler.session import CrawlerSession
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    test_training_data = TrainingData()
    test_training_data.get_high_frequency_word()
