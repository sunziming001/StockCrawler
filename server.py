import web
from WebHandle.WebIndex import WebIndex
from WebHandle.WebOpen import WebOpen
urls = ('/', 'WebIndex',
        '/open', 'WebOpen'
        )




if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
