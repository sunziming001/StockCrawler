from Spiders.StockSpiders.KLineSpider import KLineSpider


class DayKLineSpider(KLineSpider):
    name = 'DayKLineSpider'
#week http://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery112409586267286391155_1592537990001&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=103&fqt=1&secid=0.000001&beg=0&end=20500000&_=1592537990094
    # http://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery112405829661467039833_1591928624859&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt=1&secid=0.300059&beg=0&end=20500000&_=1591928625487

    def get_k_line_table_id(self):
        return 0

    def get_jquery_str(self):
        return 'jQuery112405829661467039833_1591928624859'

    def format_url(self, scode):
        url = ('http://push2his.eastmoney.com/api/qt/stock/kline/get?'
               + 'cb=jQuery112405829661467039833_1591928624859&'
               + 'fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&'
               + 'secid='+self.get_str_market_id()+'.' + scode + '&'
               + 'ut=7eea3edcaed734bea9cbfc24409ed989&'
               + 'fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&'
               + 'fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&'
               + 'klt=101&'
               + 'fqt=1&'
               + 'beg=0&'
               + 'end=20500000&'
               + '_=1591928625487')
        return url
