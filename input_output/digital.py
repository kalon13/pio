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

from PySide.QtCore import *

class Digital(QObject):
    
    value_changed = Signal(int)
    
    def __init__(self, io_module, parameters, parent=None):
        QObject.__init__(self, parent)
        
        self._io_module = io_module
        
        self.address = parameters.pop('address', 0)
        self.name = parameters.pop('name', 'Digital_{0}'.format(self.address))
        self.default_value = parameters.pop('default_value', 0)
        self.inverse_logic = parameters.pop('inverse_logic', False)
        self.parameters = parameters
        self._value = None
        
        self.value_changed.connect(self.on_value_changed)
        
    @Slot(int)
    def on_value_changed(self, value):
        self._value = value
        print(self.name, self._value)
        
    def parseValue(self, value=None, inverse=None):
        if value == None:
            value = self._value
        if inverse == None:
            inverse = self.inverse_logic
        if value == None:
            return None
        return 1 if (value>0 and not inverse) or (value==0 and inverse) else 0
        
    def __call__(self, value=None):
        if value == None:
            return self.parseValue();
        if self.parseValue() != value or self.parseValue() == None:
            self.value_changed.emit(self.parseValue(value))
            return value
    
    def __getitem__(self, name):
        if name == 'name':
            return self.name
        if name == 'value':
            return self.parseValue()
        if name == 'default_value':
            return self.default_value
        if name == 'address':
            return self.address
        try:
            return self.parameters[name]
        except:
            return None
        
    def __str__(self):
        return "{{{0}: {1}}}".format(self.name, self._value)
#     def __repr__(self):
#         return "{{{0}: {1}}}".format(self.name, self.value)

class Digital_in(Digital):
    
    def __init__(self, io_module, parameters):
        Digital.__init__(self, io_module, parameters)

class Digital_out(Digital):
    
    def __init__(self, io_module, parameters):
        Digital.__init__(self, io_module, parameters)
    
    @Slot(int)
    def change_value(self, value):
        if value != self.parseValue(self._value):
            command = dict(command = 'write',
                           parameters = dict(output = self,
                                             value = self.parseValue(value)))
            self._io_module.command_queue.put(command)
