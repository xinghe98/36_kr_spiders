import requests
import json
import time
import re
from selenium import webdriver
from lxml import etree

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "content-type": "application/json",
    "referer": "https://36kr.com/"
    # "cookie": "Hm_lvt_1684191ccae0314c6254306a8333d090=1601449704,1601453338,1601454309,1602052975; Hm_lvt_713123c60a0e86982326bae1a51083e1=1601449704,1601453338,1601454309,1602052975; acw_tc=2760827816020529883352685ef635c09bae71434d93551ecbaa5530ab97d6; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22174ddd73af56c8-0a87562e4e777a-333376b-2073600-174ddd73af6669%22%2C%22%24device_id%22%3A%22174ddd73af56c8-0a87562e4e777a-333376b-2073600-174ddd73af6669%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ss_pp_id=cf45c1ecda92da75e2a1602024840135; Hm_lpvt_1684191ccae0314c6254306a8333d090=1602054343; Hm_lpvt_713123c60a0e86982326bae1a51083e1=1602054343"
    }

"""获取pagecallback与itemid"""
def get_js(keyword):
    br = webdriver.Chrome(executable_path='./chromedriver.exe')
    br.get('https://36kr.com/search/articles/{}'.format(keyword))
    js_text = re.findall('"pageCallback":"(\w+)"',br.page_source)
    itemid = re.findall('"itemId":(\d+)',br.page_source)
    return js_text[0],itemid

"""获取后续500篇文章数据"""
def get_next(jscode,keyword):
    t = time.time()
    url = 'https://gateway.36kr.com/api/mis/nav/search/resultbytype'
    data = {"partner_id":"web","timestamp":int(t),"param":{"searchType":"article","searchWord":keyword,"sort":"date","pageSize":500,"pageEvent":1,"pageCallback":jscode,"siteId":1,"platformId":2}}
    res = requests.post(url,headers=headers,data=json.dumps(data))
    itemid = re.findall('"itemId":(\d+)',res.text)
    print("共获取{}个链接".format(str(len(itemid))))
    return itemid

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

"""加载单篇文章并保存"""
def load_page(itemid):
    url = 'https://36kr.com/p/{}'.format(itemid)
    res = requests.get(url,headers=headers)
    data = etree.HTML(res.text)
    title = data.xpath('//div[@class="common-width"]/div/h1/text()')[0]
    title = validateTitle(title)
    artice = data.xpath('//div[@class="common-width content articleDetailContent kr-rich-text-wrapper"]//text()')
    with open('./{}.txt'.format(title),'w',encoding='utf-8') as f:
        for i in artice:
            f.write(i)
    print(title,"写入完成")


if __name__ == '__main__':
    keyword = input("请输入需要搜索的关键词：")
    jscode,home_itemid = get_js(keyword)
    other_itemid = get_next(jscode,keyword)
    for i in home_itemid:
        load_page(i)
    for k in other_itemid:
        load_page(k)