from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
from selenium.webdriver.chrome.options import Options

import selenium.common.exceptions
import json
import csv
import time
import requests
import pymongo

from requests.adapters import HTTPAdapter

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


class JdSpider():
    def init(self):
        self.file_format = input('请输入文件保存格式（txt、json、csv、mongodb）：')
        while self.file_format != 'txt' and self.file_format != 'json' and self.file_format != 'csv' and self.file_format != 'mongodb':
            self.file_format = input('输入错误，请重新输入文件保存格式（txt、json、csv）：')
        if self.file_format == 'txt':
            self.file = open('Jd.txt', 'w', encoding='utf-8')
        elif self.file_format == 'json':
            self.file = open('Jd.json', 'w', encoding='utf-8')
        elif self.file_format == 'csv':
            self.file = open('Jd_less.csv', 'w', encoding='utf-8-sig', newline='')
            self.writer = csv.writer(self.file)
            self.writer.writerow(['price', 'commit', 'kind', 'products', 'goods_name', 'name'])
        elif self.file_format == 'mongodb':
            self.client = pymongo.MongoClient(host='127.0.0.1',port=27017)
        print('File Initialized')

        self.prices = []
        self.names = []
        self.commits = []
        self.content_url = []
        self.count = 0

        self.n = 0

        self.page_num = 1
        self.tree = None
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.second_page = None

        # self.start_url = 'https://search.jd.com/Search?keyword=%E6%B1%BD%E8%BD%A6%E7%94%A8%E5%93%81&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=1.his.0.0&page=197&s=5880&click=0'
        self.start_url = 'https://search.jd.com/Search?keyword=%E6%B1%BD%E8%BD%A6%E7%94%A8%E5%93%81&enc=utf-8'
        print('Data Initialized')
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('disable-infobars')
        # self.browser = webdriver.Chrome(executable_path=r'E:\谷歌驱动程序70版\chromedriver.exe')
        self.browser = webdriver.Chrome(executable_path=r'E:\谷歌驱动程序70版\chromedriver.exe',options=self.options)
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser, 10)
        print('Browser Initialized')

    def parse_page(self):
        try:
            self.n = 0
            self.prices = self.wait.until(
                # EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[2]/strong/i')))
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[3]/strong/i')))
            self.names = self.wait.until(
                # EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[3]/a/em')))
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[4]/a/em')))
            self.commits = self.wait.until(
                # EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[4]/strong')))
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[5]/strong')))
            self.content_url = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[1]/a')))
            # print(self.content_url)
        except selenium.common.exceptions.TimeoutException:
            print('parse_page:TimeoutException')
            self.parse_page()
        except selenium.common.exceptions.StaleElementReferenceException:
            print('parse_page:StaleElementReferenceException')
            self.browser.refresh()
        else:
            if len(self.prices) != 60 or len(self.names) != 60 or len(self.commits) != 60 or len(
                    self.content_url) != 60:
                print('Trying...')
                self.parse_page()

    def get_second_content(self, i):

        second_url = self.content_url[i].get_attribute('href')
        response = session.get(url=second_url, headers=self.headers)
        # response.encoding = 'gbk'
        second_page = response.content.decode('gbk', 'ignore')
        # with open('%s.html'%i,'w') as f:
        #     f.write(second_page)

        self.tree = etree.HTML(second_page)
        # kind = self.tree.xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[3]/a/text')
        kind_list = self.tree.xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[3]/a')
        kind = kind_list[0].text if kind_list else ''
        products_list = self.tree.xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[5]/a')
        products = products_list[0].text if products_list else ''
        goods_name_list = self.tree.xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[7]/a')
        goods_name = goods_name_list[0].text if goods_name_list else ''
        # print(kind)
        # print(goods_name)
        # print(products)
        '//*[@id="J_recommendGoods"]/div[2]/ul/li[2]/div[1]/a'
        goods_dic = {}
        goods_dic['kind'] = kind.strip()
        goods_dic['products'] = products.strip()
        goods_dic['goods_name'] = goods_name.strip()
        # print(goods_dic)
        return goods_dic

        # goods_dic = {}
        # second_url = self.content_url[i].get_attribute('href')
        # self.browser.get(url=second_url)
        # self.second_page = self.browser.page_source
        # kind = self.browser.find_element_by_xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[3]/a').text
        # goods_name = self.browser.find_element_by_xpath('//*[@id="crumb-wrap"]/div[1]/div[1]/div[7]/a').text
        # print(kind)
        # print(goods_name)
        # goods_dic['kind'] = kind
        # goods_dic['goods_name'] = goods_name
        # self.browser.back()
        # return goods_dic

    def write_to_file(self):
        try:
            if self.file_format == 'txt':
                for i in range(60):
                    self.count += 1
                    print('录入数据：' + str(self.count))
                    self.file.write('--------------------' + str(self.count) + '--------------------\n')
                    self.file.write('price：')
                    self.file.write(self.prices[i].text)
                    self.file.write('\n')
                    self.file.write('name：')
                    self.file.write(self.names[i].text)
                    self.file.write('\n')
                    self.file.write('commit：')
                    self.file.write(self.commits[i].text)
                    self.file.write('\n')

            elif self.file_format == 'json':
                for i in range(60):
                    self.count += 1
                    print('录入数据：' + str(self.count))
                    item = {}
                    item['price'] = self.prices[i].text
                    item['name'] = self.names[i].text
                    item['commit'] = self.commits[i].text
                    json.dump(item, self.file, ensure_ascii=False)
            elif self.file_format == 'csv':
                for i in range(60):
                    goods_content = self.get_second_content(i)
                    self.count += 1
                    print('录入数据：' + str(self.count))
                    # item = {}
                    item = goods_content
                    commit = self.commits[i].text
                    if '万' in commit:
                        commit_list = commit.split('万')
                        num = commit_list[0]
                        commit = str(int(float(num) * 1000)) + '+'

                    item['price'] = self.prices[i].text
                    item['name'] = self.names[i].text
                    item['commit'] = commit
                    # for key in item:
                    self.writer.writerow([item['price'], item['commit'], item['kind'], item['products'],
                                          item['goods_name'], item['name']])

            elif self.file_format == 'mongodb':
                for i in range(60):
                    goods_content = self.get_second_content(i)
                    self.count += 1
                    print('录入数据：' + str(self.count))
                    # item = {}
                    item = goods_content
                    commit = self.commits[i].text
                    if '万' in commit:
                        commit_list = commit.split('万')
                        num = commit_list[0]
                        commit = str(int(float(num) * 1000)) + '+'

                    item['price'] = self.prices[i].text
                    item['name'] = self.names[i].text
                    item['commit'] = commit
                    # print(item)
                    self.client.db.jd.insert_one(item)
        except selenium.common.exceptions.StaleElementReferenceException:
            print('write_to_file:StaleElementReferenceException')
            self.browser.refresh()

    def turn_page(self):
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="pn-next"]'))).click()
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")

            # print(self.page_num)
            time.sleep(3)
            # self.page_num = self.browser.find_element_by_xpath('//*[@id="J_bottomPage"]/span[1]/a[@class="curr"]').text
        except selenium.common.exceptions.NoSuchElementException:
            return True
        except selenium.common.exceptions.TimeoutException:
            print('turn_page:TimeoutException')
            while self.n < 2:
                self.n += 1
                self.turn_page()
            return True
        except selenium.common.exceptions.StaleElementReferenceException:
            print('turn_page:StaleElementReferenceException')
            self.browser.refresh()
        else:
            return False

    def close(self):
        self.browser.quit()
        print('Finished')

    def crawl(self):
        page = input('请输入爬取页数：')
        self.init()
        self.browser.get(self.start_url)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        while True:
            self.parse_page()
            self.write_to_file()
            print('第%s页录入完毕' % self.page_num)
            if self.turn_page() == True or int(page) == int(self.page_num):
                break
            self.page_num += 1
        self.close()


if __name__ == '__main__':
    spider = JdSpider()
    spider.crawl()
