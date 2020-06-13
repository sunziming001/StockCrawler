
from Spiders.StockSpiders.KLineSpider import KLineSpider


class WeekKLineSpider(KLineSpider):
    name = 'WeekKLineSpider'

    def get_k_line_table_id(self):
        return 1

    def get_jquery_str(self):
        return 'jQuery112401339825495898772_1591876244340'

    def format_url(self, scode):
        url = ('http://64.push2his.eastmoney.com/api/qt/stock/kline/get?'
               + 'cb=jQuery112401339825495898772_1591876244340&'
               + 'secid=0.' + scode + '&'
               + 'ut=7eea3edcaed734bea9cbfc24409ed989&'
               + 'fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&'
               + 'fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&'
               + 'klt=102&'
               + 'fqt=1&'
               + 'beg=0&'
               + 'end=20500000&'
               + '_=1591876244555')
        return url
