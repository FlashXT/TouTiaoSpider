#coding = utf-8
#####################################################################
#简介：分析Ajax抓取今日头条街拍美图,Version2.0.
#Author:FlashXT
#Date:2018/7/9,Monday,rainy
#Copyright © 2018–2020 FlashXT and turboMan. All rights reserved.
#####################################################################
import re
import json

import os
import requests
import pymongo
from json import JSONDecodeError
from urllib.parse import urlencode
from hashlib import md5

from bs4 import BeautifulSoup
from requests import RequestException
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
def get_gallery_url(offset,keyword):
    '''获取包含图集真实地址的response内容'''
    data = {
        'offset': offset,
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
                    # result = re.search("")
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
    if html:
        soup = BeautifulSoup(html,'lxml')
        result = soup.select('title')
        if result:
            title = result[0].get_text()
        else: title='NUll'
        # print(title)
        result= re.search('gallery: JSON.parse\("(.*?)"\)',html,re.S)
        if title and result:
            result = result.group(1).replace("\\","")
            try :
                data = json.loads(result)
                if data and 'count' in data.keys() and 'sub_images' in data.keys():
                    images = [item.get('url') for item in data.get('sub_images')]
                    return {'title':title,'url':url,'image_url':images}
                else: return None
            except : return None
    else:return None

def save_to_mongo(dic):
    if db[MONGO_TABLE].insert(dic):
        return '存储到MONGO_DB:Successful!'
    return False

def main():
    for offset in range(6):
        print("offset--->", offset*20)
        #获取每一个offset的多个图集地址
        text= get_gallery_url(offset*20,"街拍")
        #对每个图集的地址进行转化
        parsed_url = parse_gallery_url(text)
        #获取每个图集中的照片地址
        for item in parsed_url:
            html = get_image_url(item)
            try:
               result = parse_image_url(item,html)
               if result:
                   if result['image_url'] is not None:
                       print(item,save_to_mongo(result))
               else:return None
            except:continue


if __name__ == "__main__":
     main()

