from Sql.KLineTable import KLineTable, KLine
from Sql.StockBriefTable import StockBriefTable
from Sql.KLineBuyRecdTable import KLineBuyRecd
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
        ma_20_arr = []
        ma_200_arr = []
        close_arr = []
        k_line_cnt = len(k_line_list)
        for indx in range(0, k_line_cnt):
            k_line = k_line_list[indx]
            ma_20 = self.get_ma_close(indx, k_line_list, 20)
            ma_200 = self.get_ma_close(indx, k_line_list, 200)
            cur_date = datetime(k_line.year, k_line.month, k_line.day)

            date_arr.append(cur_date)
            average_cost_arr.append(k_line.cost)
            average_price_arr.append(k_line.price)
            ma_20_arr.append(ma_20)
            ma_200_arr.append(ma_200)
            close_arr.append(k_line.close)

        cost_line_data_fame = DataFrame({
            'DatetimeIndex': date_arr,
            'average_price': average_price_arr,
            'average_cost': average_cost_arr,
            'close': close_arr,
            'ma_20': ma_20_arr,
            'ma_200': ma_200_arr
        })

        plt.plot('DatetimeIndex', 'close', data=cost_line_data_fame)
        # plt.plot('DatetimeIndex', 'average_cost', data=cost_line_data_fame)
        plt.plot('DatetimeIndex', 'ma_20', data=cost_line_data_fame)
        # plt.plot('DatetimeIndex', 'ma_200', data=cost_line_data_fame)
        plt.legend()
        plt.show()

    def is_match(self, prev_k_line, cur_k_line, indx, k_line_list):
        if indx <= 2:
            return False
        cur_diff = cur_k_line.diff
        pre_diff = prev_k_line.diff

        cur_dea = cur_k_line.dea
        pre_dea = prev_k_line.dea

        macd = 2 * (cur_diff - cur_dea)
        pre_macd = 2 * (pre_diff - pre_dea)

        # macd 由负转正
        # if pre_diff < pre_dea and cur_diff > pre_diff > 0 and cur_diff > cur_dea \
        if macd > 0 > pre_macd \
                and cur_k_line.takeover + prev_k_line.takeover > 30:
            return True
        else:
            return False

    def is_sell_match(self, prev_k_line, cur_k_line):
        cur_diff = cur_k_line.diff
        pre_diff = prev_k_line.diff

        cur_dea = cur_k_line.dea
        pre_dea = prev_k_line.dea

        macd = 2 * (cur_diff - cur_dea)
        pre_macd = 2 * (pre_diff - pre_dea)

        if macd < 0:
            return True
        else:
            return False

    def is_date_sep_wrong(self, prev_k_line, cur_k_line):
        return (cur_k_line.get_date() - prev_k_line.get_date()).days > 3

    def is_date_sep_cnt(self, prev_k_line, cur_k_line, cnt):
        return (cur_k_line.get_date() - prev_k_line.get_date()).days > cnt

    def analyze_all(self, table_id=0):
        for code_id in self.scode_list:
            k_line_list = KLineTable.select_k_line_list(code_id, table_id)

            self.print_progress()
            self.cur_scode_indx += 1
            if len(k_line_list) >= 2 and self.is_match(k_line_list[-2], k_line_list[-1], -1, k_line_list):
                print("\n" + code_id + " is Match")

    def get_dea(self, indx, k_line_list):
        pre_dea = 0.0
        cur_dea = 0.0

        k_line = k_line_list[indx]
        if not hasattr(k_line, "dea"):
            for i in range(0, indx):
                cur_dea = 8 / 10 * pre_dea + 2 / 10 * self.get_diff(i, k_line_list)
                pre_dea = cur_dea
            k_line.dea = cur_dea
        return k_line.dea

    def get_diff(self, indx, k_line_list):
        k_line = k_line_list[indx]
        if not hasattr(k_line, "diff"):
            ema_long = self.get_ema(indx, k_line_list, 26)
            ema_short = self.get_ema(indx, k_line_list, 12)
            k_line.diff = ema_short - ema_long
        return k_line.diff

    def get_ema(self, indx, k_line_list, arg):
        pre_ema = 0.0
        cur_ema = 0.0
        k_line = k_line_list[indx]
        if not hasattr(k_line, ('ema' + str(arg))):

            for i in range(0, indx):
                k_line = k_line_list[i]
                cur_ema = (arg - 1) / (arg + 1) * pre_ema + 2 * k_line.close / (arg + 1)
                pre_ema = cur_ema

            setattr(k_line, ('ema' + str(arg)), cur_ema)

        return getattr(k_line, ('ema' + str(arg)))

    def get_ma_cost(self, indx, k_line_list, ma):
        sum = 0.0
        if indx + 1 < ma:
            return 0
        else:
            for i in range(0, ma):
                k_line = k_line_list[indx - i]
                sum += k_line.cost
        return sum / ma

    def get_ma_close(self, indx, k_line_list, ma):
        sum = 0.0
        if indx + 1 < ma:
            return 0
        else:
            for i in range(0, ma):
                k_line = k_line_list[indx - i]
                sum += k_line.close
        return sum / ma

    def analyze_is_stock_match(self, code_id, table_id=0):
        k_line_list = KLineTable.select_k_line_list(code_id, table_id)
        for cur_idx in range(0, len(k_line_list)):
            k_line_list[cur_idx].diff = self.get_diff(cur_idx, k_line_list)
            k_line_list[cur_idx].dea = self.get_dea(cur_idx, k_line_list)

        last_indx = len(k_line_list) - 1
        if last_indx <= 0:
            return False
        if self.is_match(k_line_list[last_indx - 1], k_line_list[last_indx], last_indx, k_line_list):
            return True
        else:
            return False

    def analyze_profit(self, code_id, table_id=0):
        k_line_list = KLineTable.select_k_line_list(code_id, table_id)
        buy_recd_list = []
        win_cnt = 0
        total_cnt = 0
        day_cnt = 0
        growth = 0
        prev_k_line = None
        is_during_check = False
        total_raise_rate = 0.0
        total_des_rate = 0.0
        start_check_k_line = None
        win_exp_rate = 0.1
        lose_exp_rate = -0.05

        for cur_idx in range(0, len(k_line_list)):
            k_line_list[cur_idx].diff = self.get_diff(cur_idx, k_line_list)
            k_line_list[cur_idx].dea = self.get_dea(cur_idx, k_line_list)

        for cur_idx in range(0, len(k_line_list)):
            k_line = k_line_list[cur_idx]

            if prev_k_line is None:
                is_during_check = False
                pass
            elif is_during_check:
                if start_check_k_line is None:
                    start_check_k_line = k_line
                    keep_trace_day = 1
                    continue
                elif start_check_k_line.open != 0:
                    total_raise_rate = (k_line.high - start_check_k_line.open) / start_check_k_line.open
                    total_des_rate = (k_line.low - start_check_k_line.open) / start_check_k_line.open
                    total_over_rate = (k_line.close - start_check_k_line.open) / start_check_k_line.open
                    if win_exp_rate >= total_raise_rate \
                            and total_des_rate >= lose_exp_rate \
                            and self.is_sell_match(prev_k_line, k_line):
                        pass
                    else:
                        is_during_check = False
                        output_rate = 0.0
                        if total_raise_rate > win_exp_rate:
                            growth = growth * (1.0 + win_exp_rate)
                            output_rate = win_exp_rate
                        elif total_des_rate < lose_exp_rate:
                            growth = growth * (1.0 + lose_exp_rate)
                            output_rate = lose_exp_rate
                        else:
                            growth = growth * (1.0 + total_over_rate)
                            output_rate = total_over_rate

                        cur_buy_recd = KLineBuyRecd()
                        cur_buy_recd.code_id = k_line.codeId
                        cur_buy_recd.buy_date = start_check_k_line.get_date_str()
                        cur_buy_recd.sell_date = k_line.get_date_str()
                        cur_buy_recd.buy_price = start_check_k_line.open
                        cur_buy_recd.sell_price = cur_buy_recd.buy_price * (1 + output_rate)
                        cur_buy_recd.days = (k_line.get_date() - start_check_k_line.get_date()).days

                        buy_recd_list.append(cur_buy_recd)
                        print(code_id + " " + start_check_k_line.get_date_str() + "~" + k_line.get_date_str() + ": "
                              + str(output_rate) + " day: " + str(cur_buy_recd.days))
                else:
                    is_during_check = False

            elif self.is_match(prev_k_line, k_line, cur_idx, k_line_list):
                is_during_check = True
                total_raise_rate = 0.0
                total_des_rate = 0.0
                start_check_k_line = None

            prev_k_line = k_line

        if is_during_check and start_check_k_line is not None:
            print("has checking stock " + k_line.codeId)
            cur_buy_recd = KLineBuyRecd()
            cur_buy_recd.code_id = k_line.codeId
            cur_buy_recd.buy_date = start_check_k_line.get_date_str()
            cur_buy_recd.buy_price = start_check_k_line.open
            cur_buy_recd.days = 0
            cur_buy_recd.sell_date = 'None'
            cur_buy_recd.sell_price = 0.0
            buy_recd_list.append(cur_buy_recd)

        return buy_recd_list

    def print_progress(self):
        str_progress = "{0}/{1}".format(str(self.cur_scode_indx),
                                        str(len(self.scode_list)))
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")
