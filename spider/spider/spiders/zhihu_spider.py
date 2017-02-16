#coding=utf-8
"""zhihu crawler"""
import scrapy
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

class ZhihuSpider(scrapy.Spider):

    name = 'zhihu'

    allowed_domains = ["www.zhihu.com"]

    # start_urls = ['https://www.zhihu.com/login/phone_num']

    rules = (
        Rule(SgmlLinkExtractor(allow=('/question/\d+#.*?', )), callback='parse_page', follow=True),
        Rule(SgmlLinkExtractor(allow=('/question/\d+', )), callback='parse_page', follow=True),
    )

    VCZH_URL = allowed_domains[0] + '/people/excited-vczh'
    start_urls = ['https://www.zhihu.com/people/excited-vczh']
    headers = {
        'User-Agent': 'Mozilla/5.0 '+
                      '(Linux; Android 6.0; Nexus 5 Build/MRA58N)'+
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'+
                      ' Chrome/57.0.2950.4 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Host': "www.zhihu.com",
        'Origin': "http://www.zhihu.com",
        'Pragma': "no-cache",
        'Referer': "http://www.zhihu.com/",
        'X-Requested-With': "XMLHttpRequest"
    }

    def parse(self, response):
        # post_login_data = {
        #     '_xsrf':self.get_xsrf(),
        #     'password':'noon70233374',
        #     'remember_me': 'true',
        #     'email': '18801731480',
        # }

        # return scrapy.FormRequest.from_response(
        #     response,
        #     formdata={post_login_data},
        #     callback=self.after_login
        # )
        print response


    def get_xsrf(self):
        '''_xsrf 是一个动态变化的参数'''
        index_url = 'https://www.zhihu.com'
        # 获取登录时需要用到的_xsrf
        index_page = scrapy.Request(
            url=index_url,
            method='GET',
            header=ZhihuSpider.headers,
        )

        print index_page
        # html = index_page.text
        # pattern = r'name="_xsrf" value="(.*?)"'
        # # 这里的_xsrf 返回的是一个list
        # _xsrf = re.findall(pattern, html)
        # return _xsrf[0]


    def after_login(self, response):
        print 'after login'
