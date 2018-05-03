#-*- coding:utf-8 -*-
'''Zheng 's BUG'''
from urllib.parse import urlencode
import json
import re
from hashlib import  md5
import os
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from multiprocessing import Pool

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        'from':'search_tab'
    }
    #字典类型转url请求参数
    #这是ajax请求的网址,不要忘了问号
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:

            return response.text
        return None
    except RequestException:
        print("请求索引出错")
        return None

def parse_page_index(html):
    data = json.loads(html)
    #如果data在键名中
    if data and 'data' in data.keys():
        #迭代data字典中的数据
        for item in data.get('data'):
            #print(item)
            yield item.get('article_url')

def get_page_detail(url):
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错", url)
        return None

def parse_page_detail(html, url):
    bsObj = BeautifulSoup(html, 'html.parser')
    title = bsObj.select('title')[0].get_text()
    #print(title)
    #数据不在正常的标签里，只能正则匹配了
    imgPattern = re.compile("gallery: JSON.parse\(\"(.*?)\"\),", re.S)
    result = re.search(imgPattern, html)
    if result is not None:
        #匹配json串数据，并解析
        #格式调整
        newResult = result.group(1).replace('\\\\', '#')
        newResult = newResult.replace('\\', '')
        newResult = newResult.replace('#', '\\\\')
        newResult = newResult.replace('\/', '/')
        #print(newResult)
        data = json.loads(newResult)
        #print(data)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            #print(sub_images)
            images = [item.get('url') for item in sub_images]
            #print(images)
            for image in images: download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images,
            }

def download_image(url):
    print("当前正在下载",url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            #content是二进制
            save_image(response.content)
        return None
    except RequestException:
        print("请求图片出错", url)
        return None

def save_image(content):
    #md5防止重复图片
    file_name = '\{0}.{1}'.format(md5(content).hexdigest(), 'jpg')
    dirpath = os.getcwd() + "\\街拍\\"
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    if not os.path.exists(dirpath+file_name):
        with open(dirpath+file_name, 'wb') as f:
            f.write(content)
            f.close()
def main(offset):
    #获得的是json形式返回的数据
    html = get_page_index(offset, '街拍')
    #print(html)

    for url in parse_page_index(html):
        #print(url)
        if url:
            html = get_page_detail(url)
            if html is not None:
                result = parse_page_detail(html, url)

                if result:
                    print(result)
                    #save()

if __name__ == '__main__':
    start = 1
    end = 20
    main(0)
    #构造一个list，设置offset参数，实现下滑加载请求
    #groups = [x*20 for x in range(start, end+1)]
    #pool = Pool()
    #需要执行的函数，可迭代对象
    #pool.map(main, groups)