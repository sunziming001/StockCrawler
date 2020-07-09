import os
import web
class WebOpen:
    def GET(self):
        i = web.input(fname=None,dirname=None)
        file_path = './recd/'+i.dirname+'/'+i.fname
        fp = open(file_path,'r')
        buff = fp.read()
        fp.close()
        return buff