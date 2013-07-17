# -*- coding: utf-8 -*-

import time
import random
from pio.iomodule import IOModule
from pio.libs import minimalmodbus

class Modbustest_module(IOModule):
    _instrument = None
     
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
        minimalmodbus.BAUDRATE = parameters['baudrate']
        minimalmodbus.TIMEOUT  = 1
        self._instrument = minimalmodbus.Instrument(parameters['port'], 1)
        if self._instrument:        
            self.opened =  True
        else:
            self.opened = False
         
    def close(self, parameters):
        self.opened = False
         
    def write(self, parameters):
        if not self.opened:
            return
        new_value = parameters['value']
        self._instrument.write_register(parameters['output']['address'], new_value)
        parameters['output'](new_value)
         
    def read(self, parameters):
        if not self.opened:
            return
        new_value = self._instrument.read_register(parameters['input']['address'])
        if new_value != parameters['input']['value']:
            parameters['input'](new_value)
