# -*- coding: utf-8 -*-

import io
import time
import logging
import serial 
from pio.iomodule import IOModule

class Advantech4050serial_module(IOModule):
     
    def __init__(self, module):
        IOModule.__init__(self, module)
        self._serial = None
        
        max_instrument = 0
        for di in self.digital_in:
            max_instrument = max([di['instrument_address'] or 0, max_instrument])
        max_instrument = max_instrument + 1
        
        self._digital_group = []
        for i in range(0, max_instrument):
            self._digital_group.append([])
        
        for di in self.digital_in:
            instrument_address = di['instrument_address'] or 0
            self._digital_group[instrument_address].append(di)
        
        self._number_of_instrument = max_instrument
        self.start_acquisition_thread()
         
    def acquisition(self):
        polling_time = self.parameters.get('polling_time', 0.1)
        while self.working_acquisition:
            for i in range(0, self._number_of_instrument):
                if len(self._digital_group[i]) > 0:
                    command = dict(command = 'read',
                                   parameters = dict(input='all',
                                                     instrument_address=i))
                    self.command_queue.put(command)
            time.sleep(polling_time)
     
    def open(self, parameters):
        try:
            port = parameters.get('port', '/dev/ttyUSB0')
            baudrate = parameters.get('baudrate', 9600)
            timeout = parameters.get('timeout', 1)
            bytesize = parameters.get('bytesize', 8)
            parity = parameters.get('parity', 'N')
            stopbits = parameters.get('stopbits', 1)
            xonxoff = parameters.get('xonxoff', 0)
            rtscts = parameters.get('rtscts', 0)
            
            self._serial = serial.Serial(port,
                                         baudrate=baudrate,
                                         bytesize=bytesize, 
                                         parity=parity,
                                         stopbits=stopbits,
                                         xonxoff=xonxoff,
                                         rtscts=rtscts,
                                         timeout=timeout)
        except:
            logging.error('Impossibile connettersi la porta {0}'.format(port))
        if self._serial:
            self._serialWrapper = io.TextIOWrapper(io.BufferedRWPair(self._serial, self._serial), 'utf-8', newline='')
            self.opened =  True
        else:
            self.opened = False
         
    def close(self, parameters=None):
        if self._serial:
            self._serial.close()
        self.opened = False
         
    def write(self, parameters):
        if not self.opened:
            return
        
        new_value = parameters['value']
        value = str(new_value).zfill(2)
        address = str(parameters['output']['address'])
        instrument_address = str(parameters['output']['instrument_address']).zfill(2)
        command = '#{0}1{1}{2}\r'.format(instrument_address, address, value)
        
#         t1 = time.time()
        self._serial.flush()
        self._serialWrapper.write(command)
        self._serialWrapper.flush()
        self._serial.read(2)
#         print(time.time() - t1)
        parameters['output'](new_value)
         
    def read(self, parameters):
        if not self.opened:
            return
        
        instrument_address = str(parameters['instrument_address']).zfill(2)
        if parameters['input'] == 'all':
            command = '${0}6\r'.format(instrument_address)
            
#             t1 = time.time()
            self._serial.flush()
            self._serialWrapper.write(command)
            self._serialWrapper.flush()
            read_byte = (self._serial.read(8)).decode('utf-8')
#             print(time.time() - t1)
            
            if not read_byte:
                logging.debug('Data empty')
                return
            if read_byte[0] == '!':
#                 data = int(read_byte[1:3], 16)
#                 for do in self.digital_out:
#                     new_value = data & (1 << int(do['address']))
#                     if new_value > 1:
#                         new_value = 1
#                     if new_value != do['value']:
#                         do(new_value)
                data = int(read_byte[3:5], 16)
                for di in self._digital_group[parameters['instrument_address']]:
                    new_value = data & (1 << int(di['address']))
                    if new_value > 1:
                        new_value = 1
                    if new_value != di['value']:
                        di(new_value)
            else:
                logging.debug('Data invalid -', read_byte, '-')
    