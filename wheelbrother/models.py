#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class VoteupAnswer(models.Model):
    '''
        赞同的答案
    '''
    userid = models.CharField(max_length=30)
    answerid = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
