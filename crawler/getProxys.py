#coding=utf-8
import time
import json
import random
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Host': "www.zhihu.com",
    'Origin': "https://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "https://www.zhihu.com/",
    'X-Requested-With': "XMLHttpRequest"
}

get_proxys_url = 'http://www.kuaidaili.com/free/intr/'

pages = 1
ip_list = list()

# while True:
#     response = requests.get(get_proxys_url+str(pages)+'/', headers=HEADERS)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     pages = pages + 1

#     items = soup.find('tbody').find_all('tr')
#     ip_dict = dict()

#     for item in items:
#         item_detail = item.find_all('td')
#         ip_dict['ip'] = item_detail[0].string
#         ip_dict['port'] = item_detail[1].string
#         ip_list.append(ip_dict)
#         print ip_dict
    
#     time.sleep(3)
#     if pages >= 50:
#         break

# with open('ip_proxy.json', 'w') as out_file:
#     json_dict = dict()
#     json_dict['ip_proxy'] = ip_list
#     json.dump(json_dict, out_file, ensure_ascii=False, indent=4)
#     print 'build data set done !'
ip_dict_json = dict()
with open('ip_proxy.json', 'r') as json_file:
    ip_dict_json = json.load(json_file)

while True:
    print random.choice(ip_dict_json['ip_proxy'])