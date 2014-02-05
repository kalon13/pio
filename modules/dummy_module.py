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

import time
import random
from pio.iomodule import IOModule

class Dummy_module(IOModule):
    def __init__(self, module):
        IOModule.__init__(self, module)
        self.start_acquisition_thread()
        
    def acquisition(self):
        polling_time = self.parameters.get('polling_time', 0.1)
        while self.working_acquisition:
            for di in self.digital_in:
                command = dict(command = 'read',
                               parameters = dict(input=di))
                self.command_queue.put(command)
            time.sleep(polling_time)
    
    def open(self, parameters):
        self.opened = True
        
    def close(self, parameters):
        self.opened = False
        
    def write(self, parameters):
        if not self.opened:
            return
        
        new_value = parameters['value']
        parameters['output'](new_value)
        
    def read(self, parameters):
        if not self.opened:
            return
        
        old_value = parameters['input']['value']
        #negate_value = 1 if old_value == 0 else 0
        #new_value = negate_value if random.random() > 0.99 else old_value
        new_value = old_value
        
        if new_value != old_value:
            parameters['input'](new_value)
            
if __name__ == '__main__':
    hc = Dummy_module(None)
    print(hc)
