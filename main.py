# coding=utf-8
import os
import getopt
import sys
from Sql.StockBriefTable import StockBriefTable
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

    print('\nusing spiders to get stock cash flow table...')
    CashFlowRecdTable.clear_cash_flow_recd_table()
    os.system("scrapy runspider Spiders/StockSpiders/CashFlowSpider.py --nolog")

    print('\nusing spiders to get stock profit table...')
    ProfitRecdTable.clear_profit_recd_table()
    os.system("scrapy runspider Spiders/StockSpiders/StockProfitSpider.py --nolog")

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


def analyzer_day_cost_profit():
    scode_list = StockBriefTable.get_stock_id_list()
    analyzer = KLineAnalyzer()
    arr = [0, 0, 0, 1.0]
    for code_id in scode_list:
        new_arr = analyzer.analyze_profit(code_id, 0, arr[0], arr[1], arr[2], arr[3])
        if new_arr[1] != arr[1]:
            arr = new_arr
            print("WinRate: " + str(arr[0] * 1.0 / arr[1]) + " Growth: " + str(arr[3]) + " day: " + str(arr[2]))


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help',
                                                   'init',
                                                   'anpv=',
                                                   'season=',
                                                   'initdl',
                                                   'initwl',
                                                   'adcost=',
                                                   'adcostall',
                                                   'adcostprofit'])
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
