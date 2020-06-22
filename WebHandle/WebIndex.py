import os


class WebIndex:
    def get_file_names(self):
        dirpath = "./recd/"
        filelist = os.listdir(dirpath)
        file_name_list = []
        for listname in filelist:
            fileabspath = os.path.join(dirpath, listname)
            if os.path.isdir(fileabspath):
                continue
            else:
                file_name_list.append(listname)
        return file_name_list

    def gen_href_text(self, file_name):
        str = '<a href=\"/open?fname=' + file_name + '\">' + file_name + '</a>'
        return str

    def GET(self):
        file_name_list = self.get_file_names()
        body_str = ''
        for file_name in file_name_list:
            body_str += self.gen_href_text(file_name) +'<br>'
        return body_str
