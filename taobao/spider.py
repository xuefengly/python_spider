import re
from selenium import  webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)#浏览器最长等待10秒

def search():#搜索方法
    try:
        browser.get("https://www.taobao.com")
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#q"))
            #获取搜索框
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        #获取搜索按钮，注意css选择器别搞错了，是首页的搜索按钮
        input.send_keys("美食")#向输入框输入“美食”
        submit.click()#点击按钮
        get_product()#调用get_product()函数获取商品信息
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total")))
        return total.text#返回total的内容
    except TimeoutError:#抛出超时错误
        return search()

def next_page(page_number):#翻页方法
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))# 获取搜索框
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()#清空页码输入框
        input.send_keys(page_number)#输入页码
        submit.click()
        get_product()  # 调用get_product()函数获取商品信息
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number)))
        #获取当前页码并判定
    except TimeoutError:
        next_page(page_number)#出错则重新调用

def get_product():#获取商品信息方法
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item")))#获取商品信息标签
    html = browser.page_source#获取网页源代码
    doc = pq(html)#使用pyquery库解析
    items = doc("#mainsrp-itemlist .items .item").items()#获取所有item标签
    for item in items:
        product = {#以字典形式保存数据
            'image': item.find('.pic .img').attr('src'),#图片链接
            'price': item.find('.price').text(),#价格
            'deal' : item.find('.deal-cnt').text()[:-3],#除去了“人付款”三个字
            'title': item.find('.title').text(),
            'shop' : item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)#输出商品信息
        save_to_mongo(product)#把商品信息存储到数据库

def save_to_mongo(result):#保存到数据库的方法
    try:
        if db[MONGO_TABLE].insert(result):#把数据插入到数据库
            print("存储到MONGODB成功",result)
    except Exception:
        print("存储到MONGODB失败",result)

def main():#主方法
    total = search()
    total = int(re.compile('(\d+)').search(total).group(1))
    """
    result = re.compile("(\d+)")#得到数字
    total = re.search(result,total).group(1)
    #re.search扫描整个字符串并返回第一个成功的匹配
    #因为正则里使用了（）,所以使用group()获取
    total = int(total)#可能是字符串，强制类型转换
    """
    for i in range(2,total +1):
        next_page(i)#从2到100页翻页
    print(total)

if __name__ == "__main__":
    main()