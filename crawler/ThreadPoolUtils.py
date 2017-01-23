#coding=utf-8
"""线程池工具类"""
from threadpool import ThreadPool, makeRequests

class MyThreadPool(object):
    """线程池工具类"""
    def __init__(self, poolsize):
        self.threadpool = ThreadPool(poolsize)

    def makeThreadRequest(self, callable_, args_list, callback=None):
        '''使用线程池来爬取用户动态'''
        thread_requests = makeRequests(callable_, args_list, callback)
        for request in thread_requests:
            self.threadpool.putRequest(request)
        self.threadpool.wait()
