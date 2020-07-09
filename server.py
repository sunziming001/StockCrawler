import web
from WebHandle.WebIndex import WebIndex
from WebHandle.WebOpen import WebOpen
from WebHandle.BrowseRecdIndex import BrowseRecdIndex
urls = ('/', 'WebIndex',
        '/browse', 'BrowseRecdIndex',
        '/open', 'WebOpen'
        )




if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
