#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class VoteupAnswer(models.Model):
    '''
        赞同的答案
    '''
    user_link = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    question_id = models.CharField(max_length=30)
    answer_id = models.CharField(max_length=30)
    answer_data_time = models.CharField(max_length=30)
    answer_content = models.CharField(max_length=1000)
    answer_vote_count = models.CharField(max_length=30)
    answer_comment_id = models.CharField(max_length=30)
