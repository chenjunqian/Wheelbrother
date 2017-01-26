#coding=utf-8
import base

class VoteupAnswer(base.BaseModel):
    '''
        赞同的答案
    '''
    user_link = object
    username = object
    question_id = object
    answer_id = object
    answer_data_time = object
    answer_content = object
    answer_vote_count = object
    answer_comment_id = object


class VoteupComment(base.BaseModel):
    '''
        赞同答案的评论
    '''
    user_link = object
    username = object
    comment_id = object
    comment_content = object
    created_time = object
    like_count = object
    dislikes_count = object
    in_reply_to_comment_id = object


class FollowQuestion(base.BaseModel):
    '''
        关注的问题
    '''
    question_id = object
    question_link = object
    question_title = object


class AnswerQuestion(base.BaseModel):
    '''
        回答的问题
    '''
    question_id = object
    question_title = object
    answer_content = object
    answer_id = object
    created_time = object
    answer_comment_id = object

class VoteupArticle(base.BaseModel):
    '''
        赞的文章
    '''
    user_link = object
    article_title = object
    # https://zhuanlan.zhihu.com/p/ + article_url_token 组成文章的连接
    article_url_token = object
    # https://www.zhihu.com/r/posts/ + article_id + /comments 组成文章评论连接
    article_id = object
    article_content = object
    created_time = object
