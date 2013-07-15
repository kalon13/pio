# -*- coding: utf-8 -*-

import time
import random
from .iomodule import *

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