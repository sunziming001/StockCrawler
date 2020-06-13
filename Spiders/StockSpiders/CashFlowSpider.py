# coding=utf-8

import scrapy
import json
from Sql.StockBriefTable import StockBriefTable
from Sql.CashFlowRecdTable import CashFlowRecdTable, CashFlowRecd


class CashFlowSpider(scrapy.Spider):
    name = 'CashFlowSpider'
    start_urls = ['http://www.cninfo.com.cn/data/project/commonInterface']
    cur_scode_indx = 0
    scode_list = StockBriefTable.get_stock_id_list()

    # 现金流表 sysapi1076
    sysapi_cash_flow_code = 'sysapi1076'

    # 一季度: rtype = 1
    # 半年:  rtype = 2
    # 三季度:  rtype = 3
    # 年度:  rtype = 4
    cur_rtype = 1

    index_str_2_type = {
        '经营活动产生的现金流量净额': 0,
        '投资活动产生的现金流量净额': 1,
        '筹资活动产生的现金流量净额': 2,
    }

    def get_cur_scode(self):
        return self.scode_list[self.cur_scode_indx]

    def start_requests(self):
        yield self.request_cash_flow(self.get_cur_scode(), 1)

    def request_cash_flow(self, code, rtype):
        return scrapy.FormRequest(url='http://www.cninfo.com.cn/data/project/commonInterface',
                                  headers={'Accept': 'application/json, text/javascript, */*; q=0.01',
                                           'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,de;q=0.6',
                                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                  formdata={'mergerMark': self.sysapi_cash_flow_code,
                                            'paramStr': 'scode=' + code + ';rtype=' + str(
                                                rtype) + ';sign=1'},
                                  callback=self.parse_cash_flow)

    def parse_cash_flow(self, response):
        data = json.loads(response.body)
        data_len = len(data)
        season = self.cur_rtype
        cash_flow_recd_list = []
        for i in range(0, data_len):
            cur_profit_data = data[i]

            for k in cur_profit_data:
                if k != 'index':
                    index_name = cur_profit_data['index']
                    cash_flow_recd = CashFlowRecd()
                    cash_flow_recd.codeId = self.get_cur_scode()
                    cash_flow_recd.season = season
                    cash_flow_recd.recd_type_id = self.index_str_2_type[index_name]
                    cash_flow_recd.year = int(k)
                    cash_flow_recd.value = cur_profit_data[k]
                    cash_flow_recd_list.append(cash_flow_recd)

        CashFlowRecdTable.insert_cash_flow_recd_list(cash_flow_recd_list)
        if self.cur_rtype != 4:
            self.cur_rtype += 1

        else:
            self.cur_scode_indx += 1
            self.cur_rtype = 1

        if self.cur_scode_indx < (len(self.scode_list) - 1):
            self.print_progress()
            yield from [self.request_cash_flow(self.get_cur_scode(), self.cur_rtype)]

    def print_progress(self):
        str_progress = "{0}/{1}: {2}".format(str(self.cur_scode_indx),
                                             str(len(self.scode_list)),
                                             str(self.cur_rtype))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
