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

class VoteupComment(models.Model):
    '''
        赞同答案的评论
    '''
    user_link = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    comment_id = models.CharField(max_length=30)
    comment_content = models.CharField(max_length=200)
    created_time = models.CharField(max_length=30)
    like_count = models.CharField(max_length=30)
    dislikes_count = models.CharField(max_length=30)
    in_reply_to_comment_id = models.CharField(max_length=30)


class FollowQuestion(models.Model):
    '''
        关注的问题
    '''
    question_id = models.CharField(max_length=30)
    question_link = models.CharField(max_length=30)
    question_title = models.CharField(max_length=60)

class AnswerQuestion(models.Model):
    '''
        回答的问题
    '''
    question_id = models.CharField(max_length=30)
    question_title = models.CharField(max_length=30)
    answer_content = models.CharField(max_length=1000)
    answer_id = models.CharField(max_length=1000)
    created_time = models.CharField(max_length=30)
    answer_comment_id = models.CharField(max_length=30)
