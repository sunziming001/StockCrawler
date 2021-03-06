# coding=utf-8
import os
import getopt
import sys
import platform
import pandas as pd
from datetime import datetime
from datetime import timedelta

from Sql.Connect import switch_amex_database, switch_nysdaq_database, switch_nyse_database, switch_zh_database
from Sql.StockBriefTable import StockBriefTable
from Sql.KLineBuyRecdTable import KLineBuyRecdTable, KLineBuyRecd

from Sql.CashFlowRecdTable import CashFlowRecdTable
from Sql.ProfitRecdTable import ProfitRecdTable
from Sql.KLineTable import KLineTable
from Analizer.StockAnalyzer import StockAnalyzer
from Analizer.KLineAnalyzer import KLineAnalyzer

import get_all_tickers.get_tickers as gt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if platform.system() == 'Windows':
    os.environ['PYTHONPATH'] = os.environ['PATH'] + BASE_DIR + ";"
else:
    os.environ['PYTHONPATH'] = os.environ['PATH'] + ":" + BASE_DIR


def help_print():
    print('get top chinese stock which has high net present value ')
    print('args:')
    print('-h\t\t\t show help')
    print('--init\t\t run before --anpv, get stocks info from network')
    print('--anpv [n]\t get top high net present value of stock, [n] means top count')


def init_us_database():
    print('start init database...')
    print('init nysdaq stock brief...')
    switch_nysdaq_database()
    gt.save_tickers(NYSE=False, NASDAQ=True, AMEX=False, filename="./data/nysdaq_stock_list.csv")
    StockBriefTable.init_stock_brief_from_cvs("./data/nysdaq_stock_list.csv")

    print('init NYSE stock brief...')
    switch_nyse_database()
    gt.save_tickers(NYSE=True, NASDAQ=False, AMEX=False, filename="./data/nyse_stock_list.csv")
    StockBriefTable.init_stock_brief_from_cvs("./data/nyse_stock_list.csv")

    print('init AMEX stock brief...')
    switch_amex_database()
    gt.save_tickers(NYSE=False, NASDAQ=False, AMEX=True, filename="./data/amex_stock_list.csv")
    StockBriefTable.init_stock_brief_from_cvs("./data/amex_stock_list.csv")

    print('\ninit finished')


def init_database():
    print('start init database...')
    print('init stock brief...')
    StockBriefTable.clear_brief_table()
    StockBriefTable.init_stock_brief_from_xl('./data/A_stock_list.xlsx')

    print('\nusing spiders to get stock cash flow table...')
    CashFlowRecdTable.clear_cash_flow_recd_table()
    os.system("scrapy runspider Spiders/StockSpiders/CashFlowSpider.py --nolog")

    print('\nusing spiders to get stock profit table...')
    ProfitRecdTable.clear_profit_recd_table()
    os.system("scrapy runspider Spiders/StockSpiders/StockProfitSpider.py --nolog")

    print('\ninit finished')


def init_day_k_line():
    print('start init day k line...')
    switch_zh_database()
    init_day_k_line_with_arg(0)
    print('\ninit finished')


def init_day_k_line_with_arg(market_id=0):
    KLineTable.clear_k_line_table(0)
    os.system("scrapy runspider Spiders/StockSpiders/DayKLineSpider.py --nolog -a market_id=" + str(market_id))


def init_us_day_k_line():
    print('start init day k line...')
    print('init nysdaq...')
    switch_nysdaq_database()
    init_day_k_line_with_arg(105)

    print('\ninit nyse...')
    switch_nyse_database()
    init_day_k_line_with_arg(106)

    print('\ninit amex...')
    switch_amex_database()
    init_day_k_line_with_arg(107)

    print('\ninit finished')


def get_rzrq():
    switch_zh_database()
    os.system("scrapy runspider Spiders/StockSpiders/RzRqSpider.py --nolog")


def init_week_k_line():
    print('start init week k line...')
    KLineTable.clear_k_line_table(1)
    os.system("scrapy runspider Spiders/StockSpiders/WeekKLineSpider.py --nolog")
    print('\ninit finished')


def init_month_k_line():
    print('start init month k line...')
    KLineTable.clear_k_line_table(2)
    os.system("scrapy runspider Spiders/StockSpiders/MonthKLineSpider.py ")
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
    min_win_rate = 2.0
    max_hold_cnt = 0
    while dt < datetime.now() + timedelta(days=2):
        buy_recd_list = KLineBuyRecdTable.select_holding_buy_recd_list_by_date(dt)
        total_price = 0.0
        average_price = 0.0
        win_cnt = 0
        recd_cnt = 0

        for buy_recd in buy_recd_list:
            total_price += buy_recd.buy_price
            if buy_recd.sell_price > buy_recd.buy_price:
                win_cnt += 1
            if buy_recd.sell_price == 0.0:
                recd_cnt -= 1
            recd_cnt += 1

        if recd_cnt > 0:
            average_price = total_price / recd_cnt
            if max_price < total_price:
                max_price = total_price
            if min_win_rate > win_cnt * 1.0 / len(buy_recd_list):
                min_win_rate = win_cnt * 1.0 / len(buy_recd_list)
            if max_hold_cnt < len(buy_recd_list):
                max_hold_cnt = len(buy_recd_list)
            print(dt.strftime("%Y-%m-%d: ") + str(total_price) + " " + str(
                win_cnt * 1.0 / recd_cnt) + " " + str(recd_cnt))
        dt = dt + timedelta(days=1)

    print("max price: " + str(max_price))
    print("max hold cnt: " + str(max_hold_cnt))
    print("min win rate: " + str(min_win_rate))


def analyzer_us_day_cost_profit():
    switch_nysdaq_database()
    analyzer_day_cost_profit()

    switch_amex_database()
    analyzer_day_cost_profit()

    switch_nyse_database()
    analyzer_day_cost_profit()


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
        buy_record_list = analyzer.analyze_profit(code_id, 0)
        has_holding = False
        for buy_record in buy_record_list:
            if buy_record.sell_date == 'None':
                has_holding = True
                continue
            rate = (buy_record.sell_price - buy_record.buy_price) / buy_record.buy_price
            growth = growth * (1 + rate)
            total_cnt += 1
            take_days += buy_record.days
            if rate > 0.0:
                win_cnt += 1
        if has_holding:
            KLineBuyRecdTable.insert_buy_recd_list(buy_record_list)
        if len(buy_record_list) > 0 and total_cnt > 0:
            print("[" + str(index) + "] WinRate: " + str(win_cnt * 1.0 / total_cnt) + " Growth: " + str(
                pow(growth, 1 / take_days)) + " days: " + str(take_days / total_cnt))


def get_buy_recd_win_rate(buy_recd_list):
    total_cnt = len(buy_recd_list) - 1
    win_cnt = 0
    if total_cnt <= 0:
        return 0.5
    else:
        for buy_recd in buy_recd_list:
            if buy_recd.sell_price > buy_recd.buy_price:
                win_cnt += 1
    return win_cnt / total_cnt


def get_buy_recd_list_sort_key(buy_recd_list):
    win_cnt = 0
    total_cnt = 0

    for buy_recd in buy_recd_list:
        if buy_recd.is_holding():
            continue
        else:
            total_cnt += 1
            if buy_recd.sell_price > buy_recd.buy_price:
                win_cnt += 1
    if total_cnt != 0:
        return round(win_cnt / total_cnt * 100, 2)
    else:
        return 0.5


def get_us_adv():
    switch_nysdaq_database()
    get_adv("nysdaq_recd")

    switch_nyse_database()
    get_adv("nyse_recd")

    switch_amex_database()
    get_adv("amex_recd")


def get_adv(dirname="zh_recd"):
    recd_list = KLineBuyRecdTable.select_holding_code()
    analyzer = KLineAnalyzer()
    buy_recd_lists_group = []
    for recd in recd_list:
        code_id = recd.code_id
        recd_list = analyzer.analyze_profit(code_id, 0, False)
        buy_recd_lists_group.append(recd_list)
    buy_recd_lists_group.sort(key=get_buy_recd_list_sort_key, reverse=True)
    str_file_name = 'recd' + datetime.now().strftime("%Y-%m-%d")
    f = open('./recd/' + dirname + '/' + str_file_name, 'w')
    f.write('<html>\n<head>\n</head>\n<body>\n')
    for buy_recd_list in buy_recd_lists_group:
        code_id = ''
        win_rate = get_buy_recd_list_sort_key(buy_recd_list)
        total_cnt = len(buy_recd_list) - 1
        if len(buy_recd_list) <= 0:
            continue
        else:
            code_id = buy_recd_list[0].code_id
        f.write('code: ' + code_id + ", win: " + str(win_rate) + "%, total cnt: " + str(total_cnt) + "<br>\n")
    f.write('\n</body></html>')


def us_daily_run():
    init_us_day_k_line()
    analyzer_us_day_cost_profit()
    get_us_adv()


def daily_run():
    init_day_k_line()
    analyzer_day_cost_profit()
    get_adv()
    get_rzrq()


def reg_test():
    dt = datetime(1991, 4, 1)
    # dt = datetime(2020, 3, 18)
    max_price = 0.0
    while dt < datetime.now() + timedelta(days=2):
        dt = dt + timedelta(days=1)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help',
                                                   'init',
                                                   'initus',
                                                   'anpv=',
                                                   'season=',
                                                   'initusdl',
                                                   'initdl',
                                                   'initwl',
                                                   'initml',
                                                   'adcost=',
                                                   'adcostall',
                                                   'adcostprofit',
                                                   'aduscostprofit',
                                                   'aholding',
                                                   'getadv',
                                                   'getusadv',
                                                   'dailyrun',
                                                   'usdailyrun',
                                                   'rzrq',
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
        elif key in ['--initus']:
            init_us_database()
        elif key in ['--initdl']:
            init_day_k_line()
        elif key in ['--initwl']:
            init_week_k_line()
        elif key in ['--initml']:
            init_month_k_line()
        elif key in ['--anpv']:
            print_top_net_present_value_stock(int(value), season)
        elif key in ['--adcostall']:
            analyzer_day_cost_all()
        elif key in ['--adcost']:
            analyzer_day_cost(value)
        elif key in ["--adcostprofit"]:
            analyzer_day_cost_profit()
        elif key in ["--aduscostprofit"]:
            analyzer_us_day_cost_profit()
        elif key in ["--aholding"]:
            analyzer_holding_info()
        elif key in ["--getadv"]:
            get_adv()
        elif key in ["--getusadv"]:
            get_us_adv()
        elif key in ["--dailyrun"]:
            daily_run()
        elif key in ["--usdailyrun"]:
            us_daily_run()
        elif key in ["--regtest"]:
            reg_test()
        elif key in ['--initusdl']:
            init_us_day_k_line()
        elif key in ["--rzrq"]:
            get_rzrq()
