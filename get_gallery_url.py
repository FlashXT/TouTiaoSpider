#coding = utf-8
#####################################################################
#简介：分析Ajax抓取今日头条街拍美图,Version1.0(爬取一个offset的多个图集的每
#     个图集的多个图片的url.)
#Author:FlashXT
#Date:2018/7/8,Sunday,cloudy
#Copyright © 2018–2020 FlashXT and turboMan. All rights reserved.
#####################################################################
import re
import json
import requests
from json import JSONDecodeError
from urllib.parse import urlencode
from requests import RequestException


def get_gallery_url(keyword):
    '''获取包含图集真实地址的response内容'''
    data = {
        'offset': 0,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        'from': 'search_tab'
    }
    params = urlencode(data)
    url =  'http://www.toutiao.com/search_content/'+'?'+params
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except RequestException:
        return "Request Error!"

def parse_gallery_url(text):
    '''通过response内容解析出图集的真实地址'''
    try:
        data = json.loads(text)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                parse_url = item.get('article_url')
                if parse_url is not None:
                    parsed_url = parse_url.replace("group/",'a')
                    yield (parsed_url)
    except JSONDecodeError:
        print("JSON Decode Error!")

def get_image_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except RequestException:
        print("Request Error!")
        return None

def parse_image_url(url,html):

    title = re.search("title: '(.*?)'",html,re.S)
    # print(title.group(1))
    result= re.search('gallery: JSON.parse\("(.*?)"\)',html,re.S)
    # print(result.group(1))
    if result:
        result = result.group(1).replace("\\","")
        data = json.loads(result)
        if data and 'count' in data.keys() and 'sub_images' in data.keys():
            count = data.get('count')
            images = [item.get('url') for item in data.get('sub_images')]
            return {'title':title.group(1),'url':url,'image_url':images}



def main():
   text= get_gallery_url("街拍")
   parsed_url = parse_gallery_url(text)
   for item in parsed_url:
       html = get_image_url(item)
       # print(html)
       result = parse_image_url(item,html)
       print(result)


if __name__ == "__main__":
    main()

