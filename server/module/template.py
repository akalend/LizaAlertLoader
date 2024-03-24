import os
from module.config import conf

class Template:

    def __ini__(self):
        self.cache = []


    def render(self, template, vars={}):

        # self.path = '/home/akalend/projects/api/src/templates/'
        mode = conf['mode']
        self.path = conf['template_path'][mode]

        file = open(self.path + template, 'r')
        txt = ''
        with file as f:
            txt = txt + f.read(4098)
            f.close()
        
        for key in vars:
            text = txt.replace('$'+key, vars.get(key, ''))
            txt = text
#            print(key)

        return txt

