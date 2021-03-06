# coding=utf-8

from abc import abstractmethod
import scrapy
import json
from datetime import datetime
from Sql.StockBriefTable import StockBriefTable
from Sql.KLineTable import KLine, KLineTable
from Sql.Connect import switch_zh_database, switch_amex_database, switch_nyse_database, switch_nysdaq_database


class KLineSpider(scrapy.Spider):
    name = 'KLineSpider'
    cur_scode_indx = 0
    scode_list = None
    str_market_id = '0'

    def __init__(self, market_id='0', *args, **kwargs):
        super(KLineSpider, self).__init__(*args, **kwargs)
        self.str_market_id = market_id
        if market_id == '0':
            switch_zh_database()
        elif market_id == '105':
            switch_nysdaq_database()
        elif market_id == '106':
            switch_nyse_database()
        elif market_id == '107':
            switch_amex_database()

        self.scode_list = StockBriefTable.get_stock_id_list()

    def get_str_market_id(self):
        return self.str_market_id

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
               + 'secid='+self.get_str_market_id()+'.' + scode + '&'
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

    def get_new_cost_info(self, last_cost_info, cur_price, take_over):
        cost_info = last_cost_info

        if cost_info is None:
            cost_info = {cur_price: take_over}
        else:
            cnt = len(cost_info)
            minus_take_over = take_over / cnt
            for price in list(cost_info.keys()):
                cost_info[price] -= minus_take_over
                if cost_info[price] <= 0:
                    del cost_info[price]

            if cost_info.get(cur_price) is None:
                cost_info[cur_price] = take_over
            else:
                cost_info[cur_price] += take_over

        return cost_info

    def get_cost_from_cost_info(self, cost_info):
        cur_average_cost_sum = 0.0
        cur_average_cost_factor = 0.0
        cur_average_cost = 0.0
        for key in cost_info.keys():
            cur_average_cost_sum += key * cost_info[key]
            cur_average_cost_factor += cost_info[key]

        if cur_average_cost_factor != 0:
            cur_average_cost = cur_average_cost_sum / cur_average_cost_factor
        else:
            cur_average_cost = cost_info[key]

        return cur_average_cost

    def parse_k_line(self, response):
        str_body = response.body.decode("utf-8", "ignore")
        head_len = len(self.get_jquery_str()) + 1
        str_json = str_body[head_len:-2]
        json_data = json.loads(str_json)
        k_line_data = None
        last_cost_info = None
        table_id = self.get_k_line_table_id()
        if json_data["data"] is not None:
            k_line_data = json_data["data"]["klines"]

        k_line_list = []

        if k_line_data is not None:
            for line in k_line_data:
                k_line_item = KLine()

                arr = line.split(',')
                dt = datetime.strptime(arr[0], '%Y-%m-%d')

                k_line_item.codeId = json_data["data"]["code"]
                k_line_item.year = dt.year
                k_line_item.month = dt.month
                k_line_item.day = dt.day
                k_line_item.open = arr[1]
                k_line_item.close = arr[2]
                k_line_item.high = arr[3]
                k_line_item.low = arr[4]
                k_line_item.takeover = arr[8]
                k_line_item.price = (float(k_line_item.open) + float(k_line_item.close) + float(
                    k_line_item.high) + float(k_line_item.low)) / 4.0

                last_cost_info = self.get_new_cost_info(last_cost_info, float(k_line_item.price),
                                                        float(k_line_item.takeover))
                k_line_item.cost = self.get_cost_from_cost_info(last_cost_info)

                k_line_list.append(k_line_item)

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
