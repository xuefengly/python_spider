import json
from multiprocessing import Pool#为实现多进程
from selenium import webdriver
import re

"""
import requests
from requests.exceptions import RequestException
#由于requests被禁止访问，使用selenium得到源码
def get_one_page(url):
    #这是一个获取url并判断是否成功的函数
    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.text#返回网页源代码
        return None#否则返回None
    except RequestException:
        return None

"""
"""
urllib库也获取不到
import urllib.request
def get_one_page(url):
    #这是一个获取url并判断是否成功的函数
    try:
        response = urllib.request.urlopen(url)
        if response.status == 200:
            print(response.read())
    except RequestException:
        return None
"""
def get_one_page(url):
    #这是一个获取url并判断是否成功的函数
    browser = webdriver.Chrome()
    try:
        browser.get(url)
        html = browser.page_source#得到网页源代码
        browser.close()#关闭测试浏览器j
        return html
    except:
        return None

def parse_one_page(html):
    #这是一个筛选函数
    pattern = re.compile('<dd>.*?board-index.*?">(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?class="star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)#添加re.S使.可以匹配换行符
    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],#去除"主演："这三个符号
            'time': item[4].strip()[5:],
            'score': item[5]+item[6]
        }
def write_to_file(content):
    #这是一个把数据存储到文件的函数
    #encoding="utf-8"和ensure_ascii=False)使数据以中文形式输出
    with open('result.txt','a',encoding="utf-8") as f:#参数a表示直接往后追加
        f.write(json.dumps(content,ensure_ascii=False)+'\n')#转成字符串形式
        f.close()

def main(offset):
    #主函数
    url = 'http://maoyan.com/board/4?offset='+str(offset)#把offset变成字符串
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':
    """
    正常抓取
    for i in range(10):
     main(i*10)
    """
    #多进程抓取
    pool = Pool()
    pool.map(main,[i*10 for i in range(10)])
