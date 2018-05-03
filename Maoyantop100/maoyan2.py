import requests
from requests.exceptions import RequestException
import re
from multiprocessing import Pool#为实现多进程
import json

headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"}

def get_one_page(url):
    # 这是一个获取url并判断是否成功的函数
   try:
       response = requests.get(url,headers=headers)
       # print(response)
       if response.status_code == 200:
           return response.text#返回网页源代码
       return None#否则返回None
   except RequestException:
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
