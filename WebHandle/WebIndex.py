import os


class WebIndex:
    def gen_href_text(self, text, dirname):
        str = '<a href=\"/browse?dirname=' + dirname + '\">' + text + '</a>'
        return str

    def GET(self):
        body = '<html><head></head><body>'
        body += self.gen_href_text("SH", "zh_recd") + '<br>'
        body += self.gen_href_text("NYSDAQ", "nysdaq_recd") + '<br>'
        body += self.gen_href_text("NYSE", "nyse_recd") + '<br>'
        body += self.gen_href_text("AMEX", "amex_recd") + '<br>'

        body +='</body></html>'
        return body
