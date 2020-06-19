# coding=utf-8


import scrapy
import json
from Sql.ProfitRecdTable import ProfitRecd, ProfitRecdTable
from Sql.StockBriefTable import StockBriefTable


class StockProfitSpider(scrapy.Spider):
    name = 'StockProfitSpider'
    start_urls = ['http://www.cninfo.com.cn/data/project/commonInterface']
    cur_scode_indx = 0
    scode_list = StockBriefTable.get_stock_id_list()

    index_str_2_type = {
        '营业收入': 0,
        '营业成本': 1,
        '营业利润': 2,
        '利润总额': 3,
        '所得税': 4,
        '净利润': 5
    }

    # 一季度: rtype = 1
    # 半年:  rtype = 2
    # 三季度:  rtype = 3
    # 年度:  rtype = 4
    cur_rtype = 1

    # 利润表 sysapi1075

    sysapi_profit_code = 'sysapi1075'

    # 现金流表 sysapi1076
    sysapi_cash_flow_code = 'sysapi1076'

    def get_cur_scode(self):
        return self.scode_list[self.cur_scode_indx]

    def start_requests(self):
        yield self.request_profit(self.get_cur_scode(), 1)

    def request_profit(self, code, rtype):
        return scrapy.FormRequest(url='http://www.cninfo.com.cn/data/project/commonInterface',
                                  headers={'Accept': 'application/json, text/javascript, */*; q=0.01',
                                           'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,de;q=0.6',
                                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                  formdata={'mergerMark': self.sysapi_profit_code,
                                            'paramStr': 'scode=' + code + ';rtype=' + str(
                                                rtype) + ';sign=1'},
                                  callback=self.parse_profit)

    # ""
    def parse_profit(self, response):
        data = []
        try:
            data = json.loads(response.body)
        except Exception:
            pass
        data_len = len(data)
        season = self.cur_rtype
        profit_recd_list = []
        for i in range(0, data_len):
            cur_profit_data = data[i]

            for k in cur_profit_data:
                if k != 'index':
                    index_name = cur_profit_data['index']
                    profit_recd = ProfitRecd()
                    profit_recd.codeId = self.get_cur_scode()
                    profit_recd.season = season
                    profit_recd.recd_type_id = self.index_str_2_type[index_name]
                    profit_recd.year = int(k)
                    profit_recd.value = cur_profit_data[k]
                    profit_recd_list.append(profit_recd)

        ProfitRecdTable.insert_profit_recd_list(profit_recd_list)
        if self.cur_rtype != 4:
            self.cur_rtype += 1

        else:
            self.cur_scode_indx += 1
            self.cur_rtype = 1

        if self.cur_scode_indx < (len(self.scode_list) - 1):
            self.print_progress()
            yield from [self.request_profit(self.get_cur_scode(), self.cur_rtype)]

    def print_progress(self):
        str_progress = "{0}/{1}: {2}".format(str(self.cur_scode_indx),
                                             str(len(self.scode_list)),
                                             str(self.cur_rtype))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
