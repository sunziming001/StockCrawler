# coding=utf-8

from abc import abstractmethod
import scrapy
import json
import os
import sys
from datetime import datetime
from Sql.StockBriefTable import StockBriefTable
from scrapy import signals
from datetime import datetime as dt


class RzRqMatchData:
    scode = ''
    date = ''
    growth = 0.0


class RzRqSpider(scrapy.Spider):
    name = 'KLineSpider'
    cur_scode_indx = 0
    scode_list = None
    date_to_match_data = {}

    def __init__(self, *args, **kwargs):
        super(RzRqSpider, self).__init__(*args, **kwargs)
        self.scode_list = StockBriefTable.get_stock_id_list()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(RzRqSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def format_url(self, scode):
        url = ('http://datacenter.eastmoney.com/api/data/get?'
               + 'type=RPTA_WEB_RZRQ_GGMX'
               + '&sty=ALL&source=WEB'
               + '&p=1'
               + '&ps=100'
               + '&st=date'
               + '&sr=-1'
               + '&var=ukyEAyba'
               + '&filter=(scode=%22' + scode + '%22)'
               + '&rt=53199626')
        return url

    def get_jquery_str(self):
        return 'var ukyEAyba='

    def get_cur_scode(self):
        return self.scode_list[self.cur_scode_indx]

    def start_requests(self):
        yield self.request_rzrq(self.get_cur_scode())

    def request_rzrq(self, code):
        url = self.format_url(code)
        return scrapy.FormRequest(url, callback=self.parse_rzrq)

    def is_match(self, pre_rzrq, cur_rzrq):
        if pre_rzrq is None or cur_rzrq is None:
            return False
        growth = (cur_rzrq["RZRQYE"] / pre_rzrq["RZRQYE"]) - 1
        return growth > 0.14

    def parse_rzrq(self, response):
        str_body = response.body.decode("utf-8", "ignore")
        head_len = len(self.get_jquery_str())
        str_json = str_body[head_len:-1]
        json_data = json.loads(str_json)
        rzrq_data = None
        cur_code_name = None
        tomorrow_rzrq = None
        if json_data["result"] is not None:
            rzrq_data = json_data["result"]["data"]

        if rzrq_data is not None:
            for rzrq in rzrq_data:
                if cur_code_name is None:
                    cur_code_name = rzrq["SCODE"]

                if self.is_match(rzrq, tomorrow_rzrq):
                    data = RzRqMatchData()
                    data.growth = (tomorrow_rzrq["RZRQYE"] / rzrq["RZRQYE"]) - 1
                    data.scode = cur_code_name
                    data.date = dt.strptime(tomorrow_rzrq["DATE"], "%Y-%m-%d %H:%M:%S")
                    date_str = data.date.strftime("%Y-%m-%d")
                    if date_str in self.date_to_match_data:
                        pass
                    else:
                        self.date_to_match_data[date_str] = []
                    self.date_to_match_data[date_str].append(data)

                tomorrow_rzrq = rzrq

        self.cur_scode_indx += 1
        if self.cur_scode_indx < (len(self.scode_list) - 1)/10:
            yield from [self.request_rzrq(self.get_cur_scode())]

    def spider_closed(self, spider):
        for date in self.date_to_match_data.keys():
            data_list = self.date_to_match_data[date]
            f = open("./recd/rzrq/recd" + date, "w")
            f.write('<html>\n<head>\n</head>\n<body>\n')
            for match_date in data_list:
                f.write('code: ' + match_date.scode + ", growth: " + str(match_date.growth) + "<br>\n")
            f.write('\n</body></html>')
