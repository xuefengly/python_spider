import requests

from requests.exceptions import RequestException

import re

import json



headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"}





def get_one_page(url):

   try:

       response = requests.get(url,headers=headers)

       # print(response)

       if response.status_code == 200:

           return response.text

       return None

   except RequestException:

       return None





def parse_one_page(html):

   pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'

                        +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'

                        +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)

                                       #re.S表示匹配任意的字符

   # print(pattern)

   items = re.findall(pattern,html)

   for item in items:

       yield {

           'index': item[0],

           'image': item[1],

           'title': item[2],

           'actor': item[3].strip()[3:],

           'time': item[4].strip()[5:],

           'score': item[5] + item[6],

       }



def write_to_file(content):

   with open("result.txt", "a", encoding='utf-8') as f:
       # print(f)
       f.write(json.dumps(content,ensure_ascii=False)+"\n")

       print(content)

       f.close()



def main(offset):

   url = 'http://maoyan.com/board/4?offset='+str(offset)

   # print(url)

   # url = 'TOP100榜 - 猫眼电影 - 一网打尽好电影

   html = get_one_page(url)

   # print(html)

   for item in parse_one_page(html):

       print(item)

       write_to_file(item)



if __name__ == '__main__':

   # p = Pool()

   # p.map(main,[i*10 for i in range(10)])

  for i in range(10):

       main(i*10)

