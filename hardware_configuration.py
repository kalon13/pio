# -*- coding: utf-8 -*-

###################################################################
# Copyright (c) 2013 Davide Marzioni
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
###################################################################

import json
import logging
import importlib
from PySide.QtCore import *
from .utils import singleton

@singleton.Singleton
class Hardware_configuration(QObject):
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.modules = []
        self.digital_in = []
        self.digital_out = []
        self.analogic_in = []
        self.analogic_out = []

    def load(self, filename):
        json_data = open(filename)
        data = json.load(json_data)
        json_data.close()
              
        for m in data['modules']:
            module = self.get_module(m)
            if not module:
                logging.error('{0} is not a module!'.format(m))
                return self
            
            self.modules.append(module)
            self.digital_in.extend(module.digital_in)
            self.digital_out.extend(module.digital_out)
            self.analogic_in.extend(module.analogic_in)
            self.analogic_out.extend(module.analogic_out)
            print(module)
        return self
        
    def get_module(self, module):
        try:
            module_type = module['access_method']['type']
            module_full_type = "{0}_module".format(module_type).capitalize()
            module_file = ".modules.{0}_module".format(module_type)
            module_lib = importlib.import_module(module_file, "pio")
            module_class = getattr(module_lib, module_full_type)
            return module_class(module)
        except Exception as e:
            logging.error(e)
        return None
    
    def reset_all(self):
        for d in self.digital_out:
            d.change_value(d['default_value'])
        for a in self.analogic_out:
            a.change_value(a['default_value'])
        
    def unload(self):
        for m in self.modules:
            m.close()
            
    def __call__(self, ad, io, name):
        search = None
        if ad == 'analogic':
            if io == 'in':
                search = self.analogic_in
            elif io == 'out':
                search = self.analogic_out
        elif ad == 'digital':
            if io == 'in':
                search = self.digital_in
            elif io == 'out':
                search = self.digital_out
        if search:
            for s in search:
                if s['name'] == name:
                    return s
        return None
        
    def __str__(self):
        return """file: {0}
moduli: {1}
di: {2}
do: {3}
ai: {4}
ao: {5}""".format(self.filename, str(self.modules), str(self.digitals_in),
                  str(self.digitals_out), str(self.analogic_in), str(self.analogic_out))
    def __unicode__(self):
        return """file: {0}
moduli: {1}
di: {2}
do: {3}
ai: {4}
ao: {5}""".format(self.filename, str(self.modules), str(self.digitals_in),
                  str(self.digitals_out), str(self.analogic_in), str(self.analogic_out))

if __name__ == '__main__':
    hc = Hardware_configuration('../cfg/hardware.json')
    print(hc)
