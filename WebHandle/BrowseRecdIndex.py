import os
import web

class BrowseRecdIndex:
    def get_file_names(self, dir):
        dirpath = './recd/'+dir+'/'
        filelist = os.listdir(dirpath)
        file_name_list = []
        for listname in filelist:
            fileabspath = os.path.join(dirpath, listname)
            if os.path.isdir(fileabspath):
                continue
            else:
                file_name_list.append(listname)
        file_name_list.sort(reverse=True)
        return file_name_list

    def gen_href_text(self, file_name,dir_name):
        str = '<a href=\"/open?fname=' + file_name + ';dirname=' + dir_name + '\">' + file_name + '</a>'
        return str

    def GET(self):
        i = web.input(dirname=None)
        file_name_list = self.get_file_names(i.dirname)
        body_str = ''
        for file_name in file_name_list:
            body_str += self.gen_href_text(file_name, i.dirname) +'<br>'
        return body_str
