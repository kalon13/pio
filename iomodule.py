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

import sys
import threading
from PySide.QtCore import *
from .input_output import digital, analogic

if sys.version > '3':
    import queue
else:
    import Queue as queue

class IOModule(QObject):
    """ Abstract class for input/output module

    Implementing class have custom function for:
    - opening/closing communication
    - read/write value
    - acquisition routine
    
    Custom class must have '_module' suffix
    """
    
    def __init__(self, module, parent=None):
        QObject.__init__(self, parent)
        
        self._elaborate_command_thread  = None
        self._acquisition_thread = None
        self.command_queue = queue.Queue()
    
        self.name = ''
        self.parameters = dict()
        self.digital_in = []
        self.digital_out = []
        self.analogic_in = []
        self.analogic_out = []
        self.working = False
        self.working_acquisition = False
        self.opened = False
        
        self.name = module['name']
        self.parameters = module['access_method']['parameters']
        
        try:
            all_di = module['digital_in']
        except:
            all_di = []
        try:
            all_do = module['digital_out']
        except:
            all_do = []
        try:
            all_ai = module['analogic_in']
        except:
            all_ai = []
        try:
            all_ao = module['analogic_out']
        except:
            all_ao = []
        
        for di in all_di:
            digital_in = digital.Digital_in(self, di)
            self.digital_in.append(digital_in)
                
        for do in all_do:
            digital_out = digital.Digital_out(self, do)
            self.digital_out.append(digital_out)
            
        for ai in all_ai:
            analogic_in = analogic.Analogic_in(self, ai)
            self.analogic_in.append(analogic_in)
             
        for ao in all_ao:
            analogic_out = analogic.Analogic_out(self, ao)
            self.analogic_out.append(analogic_out)
        
        self.start_elaborate_command_thread()
        
    def __del__(self):
        self.stop_acquisition_thread()
        self.stop_elaborate_command_thread()
        
    def elaborate_command(self):
        while self.working:
            operation = self.command_queue.get()
            if (operation['command'] == 'open'):
                self.open(operation['parameters'])
            elif (operation['command'] == 'close'):
                self.close(operation['parameters'])
                self.working = False
            elif (operation['command'] == 'read'):
                self.read(operation['parameters'])
            elif (operation['command'] == 'write'):
                self.write(operation['parameters'])
                
    def start_elaborate_command_thread(self):
        if not self.working:
            self.working = True
            self.command_queue.put(dict(command='open',
                                        parameters=self.parameters))
            self._elaborate_command_thread = threading.Thread(
                    target=self.elaborate_command)
            self._elaborate_command_thread.start()
            
                
    def stop_elaborate_command_thread(self):
        if self._elaborate_command_thread:
            self.command_queue.put(dict(command='close',
                                        parameters=self.parameters))
            self._elaborate_command_thread.join()
                
    def acquisition(self):
        raise NotImplementedError()
    
    def start_acquisition_thread(self):
        if not self.working_acquisition:
            self.working_acquisition = True
            self._acquisition_thread = threading.Thread(target=self.acquisition)
            self._acquisition_thread.start()
        
    def stop_acquisition_thread(self):
        if self._acquisition_thread:
            self.working_acquisition = False
            self._acquisition_thread.join()
    
    def open(self, parameters):
        raise NotImplementedError()
        
    def close(self, parameters):
        raise NotImplementedError()
        
    def write(self, parameters):
        raise NotImplementedError()
        
    def read(self, parameters):
        raise NotImplementedError()

    def __str__(self):
        return "{{{0}: {1}}}".format(self.name, self.__class__.__name__)
#     def __repr__(self):
#         return "{{{0}, {1}}}".format(self.name, self.__class__.__name__)
