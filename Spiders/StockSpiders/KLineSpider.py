# coding=utf-8

from abc import abstractmethod
import scrapy
import json
from datetime import datetime
from Sql.StockBriefTable import StockBriefTable
from Sql.KLineTable import KLine, KLineTable


class KLineSpider(scrapy.Spider):

    name = 'KLineSpider'
    cur_scode_indx = 0
    scode_list = StockBriefTable.get_stock_id_list()

    @abstractmethod
    def get_k_line_table_id(self):
        return 2

    @abstractmethod
    def get_jquery_str(self):
        return 'jQuery112401339825495898772_1591876244340'

    @abstractmethod
    def format_url(self, scode):
        url = ('http://64.push2his.eastmoney.com/api/qt/stock/kline/get?'
               + 'cb=jQuery112401339825495898772_1591876244340&'
               + 'secid=0.' + scode + '&'
               + 'ut=7eea3edcaed734bea9cbfc24409ed989&'
               + 'fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&'
               + 'fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&'
               + 'klt=102&'
               + 'fqt=1&'
               + 'beg=0&'
               + 'end=20500000&'
               + '_=1591876244555')
        return url


    def get_cur_scode(self):
        return self.scode_list[self.cur_scode_indx]

    def start_requests(self):
        yield self.request_k_line(self.get_cur_scode())

    def parse_k_line(self, response):
        str_body = response.body.decode("utf-8", "ignore")
        head_len = len(self.get_jquery_str())+1
        str_json = str_body[head_len:-2]
        json_data = json.loads(str_json)
        k_line_data =  None
        table_id = self.get_k_line_table_id()
        if json_data["data"] is not None:
            k_line_data = json_data["data"]["klines"]

        k_line_list = []

        if k_line_data is not None:
            for line in k_line_data:
                mkl = KLine()

                arr = line.split(',')
                dt = datetime.strptime(arr[0], '%Y-%m-%d')

                mkl.codeId = json_data["data"]["code"]
                mkl.year = dt.year
                mkl.month = dt.month
                mkl.day = dt.day
                mkl.open = arr[1]
                mkl.close = arr[2]
                mkl.high = arr[3]
                mkl.low = arr[4]
                mkl.takeover = arr[8]
                k_line_list.append(mkl)

            KLineTable.insert_k_line_list(k_line_list, table_id)

        self.cur_scode_indx += 1
        self.print_progress()
        if self.cur_scode_indx < (len(self.scode_list) - 1):
            yield from [self.request_k_line(self.get_cur_scode())]

    def request_k_line(self, code):
        url = self.format_url(code)
        return scrapy.FormRequest(url, callback=self.parse_k_line)

    def print_progress(self):
        str_progress = "{0}/{1}".format(str(self.cur_scode_indx),
                                        str(len(self.scode_list)))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
