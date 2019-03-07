# -*- coding: utf-8 -*-
import json
import time
#import winsound

import requests
import urllib
import scrapy

import logging
from scrapy.mail import MailSender
import random

from www_zhipin_com.items import WwwZhipinComItem


class ZhipinSpider(scrapy.Spider):

    handle_httpstatus_list = [302]

    name = 'zhipin'

    allowed_domains = ['www.zhipin.com']

    start_urls = [
        "http://www.zhipin.com/",
    ]

    JobKeyword = 'python'
    # positionUrl = 'https://www.zhipin.com/c101050100/?query=python'
    positionUrl = 'https://www.zhipin.com/'
    # 当前省份的下标
    currentProv = 0
    # 当前页码
    currentPage = 0
    # 当前城市的下标
    currentCity = 0 #101270600

    cityListUrl = "https://www.zhipin.com/common/data/city.json"

    cityList = []
    positionList = []

    headers = {
        #'x-devtools-emulate-network-conditions-client-id': "5f2fc4da-c727-43c0-aad4-37fce8e3ff39",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'dnt': "1",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
        #'cookie': "__c=1501326829; lastCity=101020100; __g=-; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.20.1.20.20; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502948718; __c=1501326829; lastCity=101020100; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502954829; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.21.1.21.21",
        'cache-control': "no-cache",
        #'postman-token': "76554687-c4df-0c17-7cc0-5bf3845c9831"
    }

    position_num = 0
    city_num = 0

    def parse(self, response):

        #print(response.status)
        logging.debug(response.status)
        if response.status == 302:
            #winsound.MessageBeep()
            # 等待用户输入验证码
            #input('please input verify code to continue:')
            #self.send_email('302错误', 'please input verify code to continue!')
            print('302错误', 'please input verify code to continue!')
            self.crawler.engine.close_spider(self, 'done!')
        logging.debug("request->" + response.url)
        is_one_page = response.css('div.job-list>div.page').extract()
        is_end = response.css(
            'div.job-list>div.page>a[class*="next disabled"]::attr(class)').extract()
        job_list = response.css('div.job-list>ul>li')
        for job in job_list:
            try:
                # 数据获取
                item = WwwZhipinComItem()
                # job_primary = job.css('div.job-primary')
                item['pid'] = job.css(
                    'div.info-primary>h3>a::attr(data-jid)').extract_first().strip()
                item['positionName'] = job.css(
                    'div.job-title::text').extract_first().strip()
                item['salary'] = job.css(
                    'div.info-primary>h3>a> span::text').extract_first().strip()

                info_primary = job.css('div.info-primary>p::text').extract()
                item['city'] = info_primary[0].strip()
                item['workYear'] = info_primary[1].strip()
                item['education'] = info_primary[2].strip()

                item['companyShortName'] = job.css(
                    'div.company-text>h3>a::text').extract_first().strip()
                company_info = job.css('div.company-text>p::text').extract()
                if len(company_info) == 3:
                    item['industryField'] = company_info[0].strip()
                    item['financeStage'] = company_info[1].strip()
                    item['companySize'] = company_info[2].strip()

                item['time'] = job.css(
                    'div.info-publis>p::text').extract_first().strip()
                interviewer_info = job.css('div.info-publis>h3::text').extract()
                item['interviewer'] = interviewer_info[1]

                item['updated_at'] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime())
                yield item
            except Exception:
                pass

        # 下一页不可点击则表示到底，退出
        # print(len(is_end))
        # print(len(is_one_page))
        if len(is_end) != 0 or len(is_one_page) == 0:
            # self.crawler.engine.close_spider(self, 'done!' % response.text)
            #     todo: 城市id变化，是否变化传入next_request的参数中，预先导入城市列表，然后循环
            position_num = position_num + 1
            
            if position_num == len(self.positionList):
                position_num = 0
                self.city_num += 1

            self.currentPage = 0

            if self.city_num == len(self.cityList):
                self.crawler.engine.close_spider(self, 'done!')

        # 翻页
        self.currentPage += 1

        url = self.generate_url(self.cityList[self.city_num][0], self.positionList[self.position_num][1], self.currentPage)


        time.sleep(random.randint(60,90))
        yield scrapy.http.FormRequest(url, headers=self.headers, callback=self.parse)





    def start_requests(self):
        # start_requests 只调用一次,初始化时获取city列表
        #res = requests.get(self.cityListUrl, headers=self.headers).content
        #city = json.loads(res.decode('utf-8'))
        with open('index.txt','r') as f:
            self.city_num = int(f.readline().strip())
            self.position_num = int(f.readline.strip())
            self.currentPage = int(f.readline.strip())
        self.cityList = self.get_city()
        self.positionList = self.get_position('技术')
        # 调试用
        #self.cityList = city['data']['cityList']
        url = self.generate_url(self.cityList[self.city_num][0], self.positionList[self.position_num][1], self.currentPage)

        return scrapy.http.FormRequest(url, headers=self.headers, callback=self.parse)

    def next_request(self, current_prov, current_city):
        logging.debug("current_prov"+str(current_prov))
        logging.debug("current_city"+str(current_city))
        cur_city_id = 'c' + str(self.cityList[current_prov]['subLevelModelList'][current_city]['code'])
        logging.debug(cur_city_id)
        # 这里url写想要查找什么职业
        return scrapy.http.FormRequest(
            #self.positionUrl + cur_city_id + "?query="+"%E5%B5%8C%E5%85%A5%E5%BC%8F"+("&page=%d&ka=page-%d" % (self.currentPage, self.currentPage)),
            self.positionUrl + cur_city_id + "/?query=" + urllib.parse.quote(self.JobKeyword) + ("&page=%d&ka=page-%d" % (self.currentPage, self.currentPage)),
            headers=self.headers,
            callback=self.parse)

    def send_email(self, subject, body):
        mailer = MailSender(
            smtphost = "smtp.163.com",  # 发送邮件的服务器
            mailfrom = "1xxxxxxxxx3@163.com",   # 邮件发送者
            smtpuser = "1xxxxxxxxx3@163.com",   # 用户名
            smtppass = "yxxxxxxxxxxM",  # 发送邮箱的密码不是你注册时的密码，而是授权码！！！切记！
            smtpport = 25   # 端口号
        )
        mailer.send(to="xxxxxxxxx@qq.com", subject = subject, body = body)

    def get_position(self, keyword):
        res = requests.get(self.positionUrl, headers=self.headers).content
        info = json.loads(res.decode('utf-8'))

        pos_temp = []
        #out_file = open(r'D:\Firefox Downloads\result.txt','w',encoding=r'utf-8')
        #count = 0
        for i in range(len(info['data'])):
            data = info['data'][i]['subLevelModelList']
            if(info['data'][i]['name'] == keyword):
                for j in range(len(data)):
                    list1 = data[j]['subLevelModelList']
                    for x in range(len(list1)):
                        #out_file.write(list1[x]['name']+'\n')
                        #print(list1[x]['code'])
                        #count = count + 1
                        #yield list1[x]['code']
                        pos_temp.append([list1[x]['code'], list1[x]['name']])
        return pos_temp


    def get_city(self):
        res = requests.get(self.cityListUrl, headers=self.headers).content
        info = json.loads(res.decode('utf-8'))
        info = info['data']
        pos_temp = []
        #out_file = open(r'D:\Firefox Downloads\result.txt','w',encoding=r'utf-8')
        #count = 0
        for i in range(len(info['cityList'])):
            data = info['cityList']
            #if(info['data'][i]['name'] == keyword):
            #for x in range(len(data)):
            pos_temp.append([data[i]['code'], data[i]['name']])
        return pos_temp

    def generate_url(self, city_code, position_code, page):
        with open('index.txt', 'w') as f:
            f.write(str(self.city_num)+'\n')
            f.write(str(self.position_num)+'\n')
            f.write(str(self.currentPage)+'\n')
        return 'https://www.zhipin.com/' + 'c{}'.format(city_code)+"/?query=" + urllib.parse.quote(position_code)+'&page={}&ka=page-{}'.format(page, page)