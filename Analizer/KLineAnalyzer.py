from Sql.KLineTable import KLineTable, KLine
from Sql.StockBriefTable import StockBriefTable
from datetime import datetime
import pandas as pd
from pandas import DataFrame
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt


class KLineAnalyzer:
    scode_list = StockBriefTable.get_stock_id_list()
    cur_scode_indx = 0

    def get_cur_scode(self):
        return self.scode_list[self.cur_scode_indx]

    def get_price_cost_data(self, stock_id, table_id):
        k_line_list = KLineTable.select_k_line_list(stock_id, table_id)
        map_date_2_costs = {}
        last_date = None
        cost_line_data_fame = None
        date_arr = []
        open_arr = []
        close_arr = []
        high_arr = []
        low_arr = []
        takeover_arr = []
        average_cost_arr = []
        average_price_arr = []
        for k_line in k_line_list:
            cur_date = pd.datetime(k_line.year, k_line.month, k_line.day)
            cost_info = {}
            cur_average_cost = 0.0
            cur_average_cost_sum = 0.0
            cur_average_cost_factor = 0.0
            if last_date is not None:
                cost_info = map_date_2_costs[last_date]

            cur_average_price = (k_line.open + k_line.close + k_line.high + k_line.low) / 4.0
            cur_takeover = k_line.takeover
            cost_value_count = len(map_date_2_costs)
            if cost_value_count > 0:
                minus_takeover_value = cur_takeover / cost_value_count
            else:
                minus_takeover_value = 0

            for key in list(cost_info.keys()):
                cost_info[key] -= minus_takeover_value
                if cost_info[key] <= 0:
                    del cost_info[key]

            if cost_info.get(cur_average_price) is None:
                cost_info[cur_average_price] = cur_takeover
            else:
                cost_info[cur_average_price] += cur_takeover

            for key in cost_info.keys():
                cur_average_cost_sum += key * cost_info[key]
                cur_average_cost_factor += cost_info[key]

            if cur_average_cost_factor != 0:
                cur_average_cost = cur_average_cost_sum / cur_average_cost_factor
            else:
                cur_average_cost = cost_info[key]

            date_arr.append(cur_date)
            open_arr.append(k_line.open)
            close_arr.append(k_line.close)
            high_arr.append(k_line.high)
            low_arr.append(k_line.low)
            takeover_arr.append(k_line.takeover)
            average_cost_arr.append(cur_average_cost)
            average_price_arr.append(cur_average_price)

            last_date = cur_date
            map_date_2_costs[cur_date] = cost_info

        cost_line_data_fame = DataFrame({
            'DatetimeIndex': date_arr,
            'average_price': average_price_arr,
            'average_cost': average_cost_arr
        })
        return cost_line_data_fame

    def analyze_one(self, stock_id, table_id=0):
        register_matplotlib_converters()
        cost_line_data_fame = self.get_price_cost_data(stock_id, table_id)
        plt.plot('DatetimeIndex', 'average_price', data=cost_line_data_fame)
        plt.plot('DatetimeIndex', 'average_cost', data=cost_line_data_fame)
        plt.legend()
        plt.show()

    def analyze_all(self, table_id=0):
        self.cur_scode_indx = 81
        for code_id in self.scode_list:
            price_cost_data = self.get_price_cost_data(code_id, table_id)
            l_today = None
            if len(price_cost_data) > 0:
                l_today = price_cost_data.values[-1].tolist()
            else:
                continue

            if len(l_today) == 3 and l_today[2] <= l_today[1] <= 1.01 * l_today[2]:
                print("\n" + code_id + " is Match")
            self.cur_scode_indx += 1
            self.print_progress()

    def print_progress(self):
        str_progress = "{0}/{1}".format(str(self.cur_scode_indx),
                                        str(len(self.scode_list)))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
