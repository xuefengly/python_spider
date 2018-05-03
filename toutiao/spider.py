import json
import re
from hashlib import md5
from urllib.parse import urlencode

import os
import pymongo
import requests
from bs4 import BeautifulSoup
from requests import RequestException
from config import *#即可以把config里所有的变量引入

#定义一个MongDB对象
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

#headers = {'user-agent': 'Windows / Chrome 34: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
#获取页面索引
def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
        'from': 'gallery'
        #'cur_tab': 1,
        #'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    # #urlencode可以把字典对象变成url的请求参数
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return  response.text
        return None
    except RequestException:
        print("请求页面索引出错")
        return None

#json解析函数
def parse_page_index(html):
    data = json.loads(html)#使用loads()方法把数据转换成json格式的变量（对象）
    if data and 'data' in data.keys():
        # data.keys()是json格式的data的所有键名
        #其中有两个判断，即data不为空和json格式的data变量里有data这个键名
        for item in data.get('data'):
            yield item.get('article_url')#迭data属性里每个列表的article_url

#详情页请求函数
def get_page_detail(url):
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return  response.text
        return None
    except RequestException:
        print("请求详情页出错",url)
        return None

#获取各个组图的title和属于其的列表的各种值
def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.select('title')[0].get_text()#使用css选择器,获得组图名称
    print(title)
    #image_pattern = re.compile('var gallery = (.*?)',re.S)#原视频代码
    image_pattern = re.compile('gallery: JSON.parse\(\"(.*?)\"\)')
    result = re.search(image_pattern,html)#查找是否存在image_pattern
    if result:#如果result存在
        #print(result.group(1))
        #格式调整
        newresult = result.group(1).replace('\\','')#因为得到的数据中许多地方被插入了\,替换为空格即可得到正确格式
        data = json.loads(newresult)
        #print(newresult)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')#获取键名为sub_images的值
            images = [item.get('url') for item in sub_images]#以数组形式得到组图中每张图片的url
            for image in images:#使用循环下载图片
                download_image(image)
            return {
                'title':title,
                'url':url,
                'images':images
            }
#存储到数据库函数
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):#如果result插入数据库成功
        print('存储到MongoDB成功',result)
        return True
    return False

#下载图片
def download_image(url):
    print('正在下载',url)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            save_image(response.content)#content属性返回的是二进制
        return None
    except RequestException:
        print("请求图片出错",url)
        return None
#保存图片
def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    #路径，文件名，后缀,md5()方法防止保存重复图片
    if not os.path.exists(file_path):#如果该文件不存在
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main():
   html = get_page_index(0,'街拍')
   for url in parse_page_index(html):
       #print(url)
       html = get_page_detail(url)
       #print(html)
       if html:
           result = parse_page_detail(html,url)
           save_to_mongo(result)

if __name__ == '__main__':
    main()
