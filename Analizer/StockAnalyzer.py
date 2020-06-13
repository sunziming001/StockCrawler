from Sql.ProfitRecdTable import ProfitRecdTable, ProfitRecd
from Sql.CashFlowRecdTable import CashFlowRecdTable, CashFlowRecd
from Sql.StockBriefTable import StockBriefTable
from Sql.NetPresentTable import NetPresentValue, NetPresentValueTable


class StockAnalyzer:

    @staticmethod
    def get_net_present_value_average(stock_id, season):
        value_list = NetPresentValueTable.select_net_present_value(stock_id, season)
        cnt = len(value_list)
        ret = 0.0
        is_growth = True
        last_profit_value = 0.0
        cur_profit_value = 0.0
        sum_profit = 0.0
        sum_cash_flow = 0.0
        for i in range(0, cnt):
            value_item = value_list[i]
            cur_profit_value = value_item.profit_value
            sum_profit = sum_profit + value_item.profit_value
            sum_cash_flow = sum_cash_flow + value_item.cash_flow_value

            if i == 0:
                last_profit_value = cur_profit_value
            elif is_growth:
                is_growth = cur_profit_value >= last_profit_value
                last_profit_value = cur_profit_value

        if not is_growth or sum_profit <= 0 or sum_cash_flow <= 0:
            ret = -10000.0
        else:
            ret = 1.0 * sum_cash_flow / sum_profit

        return [stock_id, ret]

    @staticmethod
    def get_net_present_value_average_growth(stock_id, season):
        sum = 0.0
        average = 0.0
        value_list = NetPresentValueTable.select_net_present_value(stock_id, season)
        last_value = 0.0
        cur_value = 0.0
        cur_growth = 0.0
        cnt = len(value_list)
        for i in range(0, cnt):
            value_item = value_list[i]
            cur_value = value_item.net_present_value
            if i == 0:
                last_value = cur_value
                continue

            if last_value == 0:
                cur_growth = -1000.0
            else:
                cur_growth = (cur_value - last_value) / last_value
            if cur_growth <= 0:
                cur_growth = -1000.0
            sum += cur_growth
            last_value = cur_value

        if cnt > 1:
            average = sum / (cnt - 1)

        return [stock_id, average]

    @staticmethod
    def get_top_net_present_value_stock(top_cnt=10, season=4):
        stock_id_list = StockBriefTable.get_stock_id_list()
        average_list = []
        stock_cnt = len(stock_id_list)
        for i in range(0, stock_cnt):
            stock_id = stock_id_list[i]
            StockAnalyzer.print_progress(str(i) + "/" + str(stock_cnt))
            average_item = StockAnalyzer.get_net_present_value_average(stock_id, season)
            average_list.append(average_item)
        average_list.sort(key=StockAnalyzer.take_second, reverse=True)

        print('\n')
        for i in range(0, top_cnt):
            tuple_item = average_list[i]
            code = tuple_item[0]
            average_growth = tuple_item[1]
            print('code: ' + code + ', average growth: ' + str(average_growth))

    @staticmethod
    def print_progress(str_progress):
        print("\b" * (len(str_progress) * 2), end="")
        print(str_progress, end="")

    @staticmethod
    def take_second(elem):
        return elem[1]

    @staticmethod
    def get_history_profit(stock_id):
        recd_cnd = ProfitRecd()
        recd_cnd.codeId = stock_id
        recd_cnd.season = 4
        recd_cnd.recd_type_id = 5
        recd_list = ProfitRecdTable.select_records(recd_cnd)
        return recd_list

    @staticmethod
    def get_history_cash_flow(stock_id):
        recd_cnd = CashFlowRecd()
        recd_cnd.codeId = stock_id
        recd_cnd.season = 4
        recd_cnd.recd_type_id = 0
        recd_list = ProfitRecdTable.select_records(recd_cnd)
        return recd_list

    @staticmethod
    def get_stock_average_profit_growth(stock_id):
        profit_recd_list = StockAnalyzer.get_history_profit(stock_id)
        recd_cnt = len(profit_recd_list)
        last_profit = 0
        cur_profit = 0
        average_growth = 0.0
        growth_sum = 0.0
        all_growth_value = []
        for j in range(0, recd_cnt):
            cur_recd = profit_recd_list[j]
            if j == 0:
                last_profit = cur_recd.value
                continue
            else:
                cur_profit = cur_recd.value
                growth = 0
                if last_profit != 0:
                    growth = 1.0 * (cur_profit - last_profit) / last_profit

                all_growth_value.append(growth)
                last_profit = cur_profit

            for growth_value in all_growth_value:
                growth_sum += growth_value

            average_growth = growth_sum * 1.0 / len(all_growth_value)

        return stock_id, average_growth

    @staticmethod
    def get_top_profit_rate_stock(top_cnt=10):
        stock_id_list = StockBriefTable.get_stock_id_list()
        stock_id_cnt = len(stock_id_list)
        stock_2_average_growth_list = []

        for i in range(0, stock_id_cnt):
            StockAnalyzer.print_progress(str(i) + '/' + str(stock_id_cnt))
            stock_id = stock_id_list[i]
            tuple_item = StockAnalyzer.get_stock_average_profit_growth(stock_id)
            stock_2_average_growth_list.append(tuple_item)

        stock_2_average_growth_list.sort(key=StockAnalyzer.take_second, reverse=True)

        for i in range(0, top_cnt):
            tuple_item = stock_2_average_growth_list[i]
            code = tuple_item[0]
            average_growth = tuple_item[1]
            print('code: ' + code + ', average growth: ' + str(average_growth))
