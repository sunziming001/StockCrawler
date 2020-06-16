# coding=utf-8
import os
import getopt
import sys
from datetime import datetime
from datetime import timedelta

from Sql.StockBriefTable import StockBriefTable
from Sql.KLineBuyRecdTable import KLineBuyRecdTable, KLineBuyRecd

from Sql.CashFlowRecdTable import CashFlowRecdTable
from Sql.ProfitRecdTable import ProfitRecdTable
from Sql.KLineTable import KLineTable
from Analizer.StockAnalyzer import StockAnalyzer
from Analizer.KLineAnalyzer import KLineAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PYTHONPATH'] = os.environ['PATH'] + BASE_DIR + ";"


def help_print():
    print('get top chinese stock which has high net present value ')
    print('args:')
    print('-h\t\t\t show help')
    print('--init\t\t run before --anpv, get stocks info from network')
    print('--anpv [n]\t get top high net present value of stock, [n] means top count')


def init_database():
    print('start init database...')
    print('init stock brief...')
    StockBriefTable.clear_brief_table()
    StockBriefTable.init_stock_brief_from_xl('./data/A_stock_list.xlsx')

    # print('\nusing spiders to get stock cash flow table...')
    # CashFlowRecdTable.clear_cash_flow_recd_table()
    # os.system("scrapy runspider Spiders/StockSpiders/CashFlowSpider.py --nolog")

    # print('\nusing spiders to get stock profit table...')
    # ProfitRecdTable.clear_profit_recd_table()
    # os.system("scrapy runspider Spiders/StockSpiders/StockProfitSpider.py --nolog")

    print('\ninit finished')


def init_day_k_line():
    print('start init day k line...')
    KLineTable.clear_k_line_table(0)
    os.system("scrapy runspider Spiders/StockSpiders/DayKLineSpider.py  --nolog")
    print('\ninit finished')


def init_week_k_line():
    print('start init week k line...')
    KLineTable.clear_k_line_table(1)
    os.system("scrapy runspider Spiders/StockSpiders/WeekKLineSpider.py --nolog")
    print('\ninit finished')


def print_top_net_present_value_stock(top_cnt, season):
    StockAnalyzer.get_top_net_present_value_stock(top_cnt, season)


def analyzer_day_cost(code_id):
    analyzer = KLineAnalyzer()
    analyzer.analyze_one(code_id, 0)


def analyzer_day_cost_all():
    analyzer = KLineAnalyzer()
    analyzer.analyze_all(0)


def analyzer_holding_info():
    dt = datetime(1991, 4, 1)
    # dt = datetime(2020, 3, 18)
    max_price = 0.0
    while dt < datetime.now() + timedelta(days=2):
        buy_recd_list = KLineBuyRecdTable.select_holding_buy_recd_list_by_date(dt)
        total_price = 0.0
        average_price = 0.0
        win_cnt = 0
        recd_cnt = len(buy_recd_list)

        for buy_recd in buy_recd_list:
            total_price += buy_recd.buy_price
            if buy_recd.sell_price > buy_recd.buy_price:
                win_cnt += 1
            if buy_recd.sell_price == 0.0:
                recd_cnt -= 1

        if recd_cnt > 0:
            average_price = total_price / recd_cnt
            if max_price < total_price:
                max_price = total_price
            print(dt.strftime("%Y-%m-%d: ") + str(total_price) + " " + str(
                win_cnt * 1.0 / len(buy_recd_list)) + " " + str(len(buy_recd_list)))
        dt = dt + timedelta(days=1)

    print("max price: " + str(max_price))


def analyzer_day_cost_profit():
    scode_list = StockBriefTable.get_stock_id_list()
    analyzer = KLineAnalyzer()
    code_cnt = len(scode_list)
    win_cnt = 0
    total_cnt = 0
    growth = 1.0
    take_days = 0
    KLineBuyRecdTable.clear_table()
    for index in range(0, code_cnt):
        code_id = scode_list[index]
        buy_record_list = analyzer.analyze_profit(code_id)
        for buy_record in buy_record_list:
            if buy_record.sell_date == 'None':
                continue
            rate = (buy_record.sell_price - buy_record.buy_price) / buy_record.buy_price
            growth = growth * (1 + rate)
            total_cnt += 1
            take_days += buy_record.days
            if rate > 0.0:
                win_cnt += 1

        KLineBuyRecdTable.insert_buy_recd_list(buy_record_list)
        if len(buy_record_list) > 0 and total_cnt > 0:
            print("[" + str(index) + "] WinRate: " + str(win_cnt * 1.0 / total_cnt) + " Growth: " + str(
                growth / take_days) + " days: " + str(take_days / total_cnt))


def get_adv():
    recd_list = KLineBuyRecdTable.select_holding_code()
    for recd in recd_list:
        code_id = recd.code_id
        buy_recd_list = KLineBuyRecdTable.select_holding_buy_recd_list_by_code_id(code_id)
        print(code_id + ": " + str(recd.buy_price))
        cnt = len(buy_recd_list)
        win_cnt = 0
        max_during = 0
        total_days = 0
        aver_during = 0

        for buy_recd in buy_recd_list:
            if buy_recd.sell_price > buy_recd.buy_price:
                win_cnt += 1
            if max_during <= buy_recd.days:
                max_during = buy_recd.days
            total_days += buy_recd.days
            # print("\tdate: " + buy_recd.buy_date + " during: " + str(buy_recd.days) + " growth: " + str((
            #           buy_recd.sell_price - buy_recd.buy_price) / buy_recd.buy_price))
        aver_during = total_days / cnt
        win_rate = win_cnt / cnt
        print("win_rate: " + str(win_rate) + " aver_dur: " + str(aver_during) + " max_dur:" + str(max_during))
        print(" ")


def daily_run():
    init_day_k_line()
    analyzer_day_cost_profit()
    get_adv()


def reg_test():
    dt = datetime(1991, 4, 1)
    # dt = datetime(2020, 3, 18)
    max_price = 0.0
    while dt < datetime.now() + timedelta(days=2):
        dt = dt + timedelta(days=1)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help',
                                                   'init',
                                                   'anpv=',
                                                   'season=',
                                                   'initdl',
                                                   'initwl',
                                                   'adcost=',
                                                   'adcostall',
                                                   'adcostprofit',
                                                   'aholding',
                                                   'getadv',
                                                   'dailyrun',
                                                   'regtest'])
    season = 4
    for key, value in opts:
        if key in ['--season']:
            season = int(value)
            if season < 0 or season > 4:
                print("season value has to be one of 1 ,2, 3, 4\n")
                exit(0)

    for key, value in opts:
        if key in ['-h', '--help']:
            help_print()
        elif key in ['--init']:
            init_database()
        elif key in ['--initdl']:
            init_day_k_line()
        elif key in ['--initwl']:
            init_week_k_line()
        elif key in ['--anpv']:
            print_top_net_present_value_stock(int(value), season)
        elif key in ['--adcostall']:
            analyzer_day_cost_all()
        elif key in ['--adcost']:
            analyzer_day_cost(value)
        elif key in ["--adcostprofit"]:
            analyzer_day_cost_profit()
        elif key in ["--aholding"]:
            analyzer_holding_info()
        elif key in ["--getadv"]:
            get_adv()
        elif key in ["--dailyrun"]:
            daily_run()
        elif key in ["--regtest"]:
            reg_test()
