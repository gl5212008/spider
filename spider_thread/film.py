import requests   # 扩展模块
                  # urllib python语言用来访问网页的模块
from threading import currentThread
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import csv
import time
start = time.time()
f = open('./film.csv','w',encoding='utf-8-sig',newline='')
write = csv.writer(f)
write.writerow(['name','url'])


headers = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Referer': 'http://db.pharmcube.com/database/cfda',
    # 'X-Requested-With': 'XMLHttpRequest'

}

def get_page(url):
    # print('<线程%s> get %s' %(currentThread(),url))
    respone=requests.get(url,headers=headers)
    # print(respone.text.encode("latin1").decode("gbk"))
    respone.encoding = 'GBK'
    # print(respone.text  )
    return {'url':url,'text':respone.text}

def callback(ret):  # 子线程或者子进程执行
    # print('____',currentThread())
    # print(ret.result()['text'])
    tree = etree.HTML(ret.result()['text'])
    b_list = tree.xpath('//div[@class="co_content8"]/ul//table//tr[2]//td[2]//b')
    # '//*[@id="header"]/div/div[3]/div[3]/div[2]/div[2]/div[2]/ul/table[1]/tbody/tr[2]/td[2]/b/a[2]'
    for b in b_list:
        name = b.xpath('.//text()')[1]
        url = 'http://www.ygdy8.net'+ b.xpath('.//a/@href')[0]
        # print(name)
        # print(url)
        write.writerow([name,url])

# urls=[
#         'https://www.baidu.com',
#         'https://www.python.org',
#         'https://www.openstack.org',
#         'https://help.github.com/',
#         'http://www.sina.com.cn/'
#     ]
# print('主线程 : ',currentThread())
url = 'http://www.ygdy8.net/html/gndy/dyzz/list_23_%s.html'
tp = ThreadPoolExecutor(10)
t_lst = []
for i in range(1,190):
    t = tp.submit(get_page,url%i).add_done_callback(callback)
tp.shutdown()
print('爬取结束')
print(time.time()-start)