#coding=utf-8
"""crawl zhi hu website """
import re
import time
import os.path
from PIL import Image

HEADERS = {
    'User-Agent': 'Mozilla/5.0 '+
                  '(X11; Linux x86_64) AppleWebKit/537.36 '+
                  '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/",
    'X-Requested-With': "XMLHttpRequest"
}

class Login(object):
    '''登录知乎'''
    def __init__(self, session):
        self.session = session

    def login(self, account, password):
        """登录知乎"""
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf':self.get_xsrf(),
            'password':password,
            'remember_me': 'true',
            'email': account,
        }

        try:
            login_page = self.session.post(post_url, data=post_data, headers=HEADERS)
            login_code = login_page.text
            print login_page.status_code
            print login_code
        except:
            # 需要输入验证码后才能登录成功
            postdata = {}
            postdata["captcha"] = self.get_captcha()
            login_page = self.session.post(post_url, data=postdata, headers=HEADERS)
            login_code = eval(login_page.text)
            print login_code['msg']

        self.session.cookies.save()

    def is_login(self):
        '''通过查看用户个人信息来判断是否已经登录'''
        url = "https://www.zhihu.com/settings/profile"
        login_code = self.session.get(url, headers=HEADERS, allow_redirects=False).status_code
        if login_code == 200:
            return True
        else:
            return False


    def get_captcha(self):
        ''' 获取验证码'''
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.session.get(captcha_url, headers=HEADERS)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print (u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha\n>")
        return captcha


    def get_xsrf(self):
        '''_xsrf 是一个动态变化的参数'''
        index_url = 'https://www.zhihu.com'
        # 获取登录时需要用到的_xsrf
        index_page = self.session.get(index_url, headers=HEADERS)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 这里的_xsrf 返回的是一个list
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]
