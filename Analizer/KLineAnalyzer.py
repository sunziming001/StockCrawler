from Sql.KLineTable import KLineTable, KLine
from Sql.StockBriefTable import StockBriefTable
from Sql.KLineBuyRecdTable import KLineBuyRecd
from Sql.ProfitRecdTable import ProfitRecdTable
from datetime import datetime
from datetime import timedelta
import pandas as pd
from pandas import DataFrame
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import talib


def get_k_line_date(k_line):
    return k_line.get_date()


class KLineAnalyzer:
    scode_list = StockBriefTable.get_stock_id_list()
    cur_scode_indx = 0
    macd_peroid = 52

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

    def is_cross(self, indx, k_line_list):
        if indx <= 0 or indx >= len(k_line_list):
            return False
        else:
            cur_k_line = k_line_list[indx]
            pre_k_line = k_line_list[indx - 1]
            return cur_k_line.diff > cur_k_line.dea and pre_k_line.dea > pre_k_line.diff and cur_k_line.diff > pre_k_line.diff

    def is_sell_cross(self, indx, k_line_list):
        if indx <= 0 or indx >= len(k_line_list):
            return True
        else:
            cur_k_line = k_line_list[indx]
            return cur_k_line.diff < cur_k_line.dea

    def is_in_up_trend(self, date, k_line_list):
        for idx in range(0, len(k_line_list)):
            k_line = k_line_list[idx]

            start_date = k_line.get_date()
            end_date = start_date + timedelta(weeks=4)
            if start_date <= date <= end_date:
                return k_line.takeover > 180
        return False

    def is_match(self, indx, k_line_list, upper_k_line_list):
        peroid = 20
        if indx <= peroid:
            return False
        # cur_diff = k_line_list[indx].diff
        # ma_close = self.get_ma_close(indx, k_line_list, 200)
        cur_k_line = k_line_list[indx]
        pre_k_line = k_line_list[indx - 1]
        if self.is_cross(indx, k_line_list) \
                and k_line_list[indx].diff <= -1.2:

            return True
        else:
            return False

    def is_sell_match(self, indx, k_line_list):
        return self.is_sell_cross(indx, k_line_list)

    def get_macd(self, df_close_data, fastperiod=12, slowperiod=26):
        diff, dea, bar = talib.MACD(
            df_close_data, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=9)
        return diff, dea, bar

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

    def is_stock_profit(self, profit_recd_list, date):
        cur_date = date - timedelta(days=180)
        cur_season = 1
        has_recd = False
        is_profit = True
        if cur_date.month <= 3:
            cur_season = 1
        elif cur_date.month <= 6:
            cur_season = 2
        elif cur_date.month <= 9:
            cur_season = 3
        else:
            cur_season = 4

        for recd in profit_recd_list:
            if recd.year < cur_date.year or (recd.year == cur_date.year and recd.season <= cur_season):
                has_recd = True
                if recd.profit <= 0:
                    is_profit = False

        return is_profit and has_recd

    def add_macd_to_k_line_list(self, k_line_list):
        close_arr = []
        for cur_idx in range(0, len(k_line_list)):
            close_arr.append(k_line_list[cur_idx].close)

        df_close = DataFrame({'close': close_arr})
        diff, dea, bar = self.get_macd(df_close['close'])

        for cur_idx in range(0, len(k_line_list)):
            k_line_list[cur_idx].diff = diff[cur_idx]
            k_line_list[cur_idx].dea = dea[cur_idx]
            k_line_list[cur_idx].bar = bar[cur_idx]

    def analyze_profit(self, code_id, table_id=0):
        k_line_list = KLineTable.select_k_line_list(code_id, table_id)
        k_line_list.sort(key=get_k_line_date)

        uper_k_line_list = KLineTable.select_k_line_list(code_id, table_id + 2)
        uper_k_line_list.sort(key=get_k_line_date)

        buy_recd_list = []
        growth = 0
        prev_k_line = None
        is_during_check = False
        start_check_k_line = None
        win_exp_rate = 10 / 100
        lose_exp_rate = -10 / 100

        if len(k_line_list) == 0:
            return buy_recd_list

        self.add_macd_to_k_line_list(k_line_list)
        self.add_macd_to_k_line_list(uper_k_line_list)

        for cur_idx in range(0, len(k_line_list)):
            k_line = k_line_list[cur_idx]

            # 002458 2018-02-28~2018-03-01: -0.1 day: 1
            if k_line.codeId == '2458' and k_line.year == 2018 and k_line.month == 2 and k_line.day == 28:
                print("11")

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
                            and not self.is_sell_match(cur_idx, k_line_list):
                        pass
                    else:
                        is_during_check = False
                        output_rate = 0.0
                        if total_raise_rate > win_exp_rate:
                            growth = growth * (1.0 + win_exp_rate)
                            output_rate = win_exp_rate
                        elif self.is_sell_match(cur_idx, k_line_list):
                            growth = growth * (1.0 + total_over_rate)
                            output_rate = total_over_rate
                        else:
                            growth = growth * (1.0 + lose_exp_rate)
                            output_rate = lose_exp_rate

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

            elif self.is_match(cur_idx, k_line_list, uper_k_line_list):
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
