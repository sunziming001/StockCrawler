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

    def analyze_one(self, stock_id, table_id=0):
        register_matplotlib_converters()

        k_line_list = KLineTable.select_k_line_list(stock_id, table_id)
        date_arr = []
        average_price_arr = []
        average_cost_arr = []
        for k_line in k_line_list:
            cur_date = datetime(k_line.year, k_line.month, k_line.day)

            date_arr.append(cur_date)
            average_cost_arr.append(k_line.cost)
            average_price_arr.append(k_line.price)

        cost_line_data_fame = DataFrame({
            'DatetimeIndex': date_arr,
            'average_price': average_price_arr,
            'average_cost': average_cost_arr
        })

        plt.plot('DatetimeIndex', 'average_price', data=cost_line_data_fame)
        plt.plot('DatetimeIndex', 'average_cost', data=cost_line_data_fame)
        plt.legend()
        plt.show()

    def is_match(self, prev_k_line, cur_k_line):
        return cur_k_line.price > cur_k_line.cost > prev_k_line.cost > prev_k_line.price

    def is_sell_match(self, prev_k_line, cur_k_line):
        return cur_k_line.price < cur_k_line.cost < prev_k_line.cost < prev_k_line.price

    def is_date_sep_wrong(self, prev_k_line, cur_k_line):
        return (cur_k_line.get_date() - prev_k_line.get_date()).days > 3

    def is_date_sep_cnt(self, prev_k_line, cur_k_line, cnt):
        return (cur_k_line.get_date() - prev_k_line.get_date()).days > cnt

    def analyze_all(self, table_id=0):
        self.cur_scode_indx = 419
        for code_id in self.scode_list:
            k_line_list = KLineTable.select_k_line_list(code_id, table_id)

            self.print_progress()
            self.cur_scode_indx += 1
            if len(k_line_list) >= 2 and self.is_match(k_line_list[-2], k_line_list[-1]):
                print("\n" + code_id + " is Match")

    def get_ma_price(self, indx, k_line_list, ma):
        sum = 0.0
        if indx + 1 < ma:
            return 0
        else:
            for i in range(0, ma):
                k_line = k_line_list[indx - i]
                sum += k_line.price
        return sum / ma

    def analyze_profit(self, code_id, table_id=0, win_cnt=0, total_cnt=0, day_cnt=0, growth=0):
        k_line_list = KLineTable.select_k_line_list(code_id, table_id)
        prev_k_line = None
        is_during_check = False
        keep_trace_day = 0
        total_raise_rate = 0.0
        total_des_rate = 0.0
        start_check_k_line = None
        pre_rase_rate = 0.0
        win_exp_rate = 0.03
        lose_exp_rate = -0.3
        match_dur_cnt = 0
        cur_indx = -1
        for cur_indx in range(0, len(k_line_list)):
            k_line = k_line_list[cur_indx]
            ma_price = self.get_ma_price(cur_indx, k_line_list, 200)
            low_cur = k_line.low
            low_prev = 0.0
            low_prev_prev = 0.0

            if (cur_indx >= 2):
                low_prev = k_line_list[cur_indx - 1].low
                low_prev_prev = k_line_list[cur_indx - 2].low

            if k_line.year <= 2017:
                prev_k_line = k_line
                continue

            #if k_line.year == 2019 and k_line.month == 3 and k_line.day == 8 and k_line.codeId == '50':
             #   print("11")

            if prev_k_line is None:
                prev_k_line = k_line
            elif self.is_date_sep_wrong(prev_k_line, k_line):
                is_during_check = False
                prev_k_line = k_line
                pass
            elif is_during_check:
                if start_check_k_line is None:
                    start_check_k_line = k_line
                    if start_check_k_line.open < prev_k_line.close:
                        is_during_check = False
                    keep_trace_day = 1
                    prev_k_line = k_line
                    continue
                elif start_check_k_line.open != 0:
                    total_raise_rate = (k_line.high - start_check_k_line.open) / start_check_k_line.open
                    total_des_rate = (k_line.close - start_check_k_line.open) / start_check_k_line.open

                    # if self.is_date_sep_wrong(prev_k_line, k_line): #date error
                    #    is_during_check = False

                    if win_exp_rate >= total_raise_rate \
                            and total_des_rate >= lose_exp_rate \
                            and k_line.close >= k_line.cost:  # keep check
                        keep_trace_day += 1
                    else:
                        is_during_check = False
                        output_rate = 0.0

                        total_cnt += 1
                        day_cnt += keep_trace_day
                        if total_raise_rate >= win_exp_rate:
                            win_cnt += 1
                            growth = growth * (1.0 + win_exp_rate)
                            output_rate = win_exp_rate
                        else:
                            growth = growth * (1.0 + total_des_rate)
                            output_rate = total_des_rate

                        print(code_id + " " + start_check_k_line.get_date_str() + "~" + k_line.get_date_str() + ": "
                              + str(keep_trace_day) + ", " + str(output_rate))
            elif k_line.price > k_line.cost : #\
                    #and k_line.price > prev_k_line.price \
                    #and low_cur > low_prev > low_prev_prev \
                    #and (low_cur - low_prev_prev)/low_prev_prev <= pre_rase_rate:
                if self.is_match(prev_k_line, k_line):
                    match_dur_cnt = 1
                elif match_dur_cnt >= 1:
                    match_dur_cnt += 1
                    if match_dur_cnt == 5:
                        is_during_check = True
                        keep_trace_day = 0
                        total_raise_rate = 0.0
                        total_des_rate = 0.0
                        start_check_k_line = None
                        match_dur_cnt = 0
            else:
                is_during_check = False
                match_dur_cnt = 0

            prev_k_line = k_line

        return [win_cnt, total_cnt, day_cnt, growth]

    def print_progress(self):
        str_progress = "{0}/{1}".format(str(self.cur_scode_indx),
                                        str(len(self.scode_list)))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
