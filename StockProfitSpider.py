import scrapy


class StockProfitSpider(scrapy.Spider):
    name = "StockProfitSpider"
    start_urls = ['http://www.cninfo.com.cn/new/disclosure/stock?tabName=data&plate=szse&stockCode=000001&type=market']

    def parse(self, response):
        for title in response.css('.post-header>h2'):
            yield {'title': title.css('a ::text').get()}

        for next_page in response.css('a.next-posts-link'):
            yield response.follow(next_page, self.parse)
