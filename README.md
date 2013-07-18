# PIO: A Python I/O library #

## What it does ##
It manages the input/output of a board using a simple json file as descriptor.
It dinamically loads the module needed to manage the hardware and it set up an acquiring cycle.
Thanks to signal-slot method you can be notified when an input changes.

#### Core dependencies ####
* libqtcore4
* Python 2 or Python 3
* Pyside (core) of the right version of python (python-pyside.qtcore or python3-pyside.qtcore)

##### Optional dependencies to make some modules work #####
* PySerial of the right version of python (python-serial or python3-serial)
* Minimalmodbus is included

Despite PIO core functionality works with both Python 2 and 3, it is designed using Python3 so some modules doesn't work with Python2.
I hope I can works on backward compatibility soon.

## How it works ##

1. Write the json hardware descriptor
2. Load the json file on Hardware_configuration instance on your main function
3. Connect your application button/function/etc... to Hardware_configuration digitals and analogics using a name
4. Done

### JSON file ###

Example of json hardware file

```
{
  "modules": [
    {
      "name": "A Simple board",
      "description": "",
      "digital_in": [
        {
          "name": "input00",
          "address": 0,
          "default_value": 0,
        },
        {
          "name": "input01",
          "default_value": 0,
          "address": 1,
        }
      ],
      "digital_out" : [
        {
          "name": "output00",
          "address": 2,
          "default_value": 0,
        },
        {
          "name": "output01",
          "address": 3,
          "default_value": 0,
        }
      ],
      "access_method" : {
        "type": "custom_serial_module",
        "parameters": {
        "port": "/dev/ttyUSB0",
        "baudrate": 115200
      }
    }
  ]
}
```

### Load ###

Hardware_configuration is singleton so be carefull to call always .Instance()

```python
from pio.hardware_configuration import Hardware_configuration

hardware = Hardware_configuration.Instance().load('an/amazing/path/to/hardware.json')
hardware.reset_all() # Set input/output to default value
```

### Connect ###

To change an output value use the function change_value(new_value):

```python
from pio.hardware_configuration import Hardware_configuration

hardware = Hardware_configuration.Instance()

hardware('digital', 'out', 'output00').change_value(1)
```

To receive an input change connect to value_changed signal:

```python
from pio.hardware_configuration import Hardware_configuration
from PySide.QtCore import *
import time

class My_Object(QObject):
  def __init__(self, parent=None):
    QObject.__init__(self, parent)
    self.hardware = Hardware_configuration.Instance()
    self.hardware('digital', 'in', 'input00').value_changed.connect(an_input_is_changed)
    self.hardware('digital', 'in', 'input01').value_changed.connect(an_input_is_changed)
    
  @Slot(int)
  def an_input_is_changed(value):
    # Print the new value to standard output
    print value

# Instantiate My_Object and simply wait
my_object = My_Object()
while True:
  time.sleep(1)
```
## License ##
This software is release under [MIT] (http://opensource.org/licenses/MIT) license.

## Special thanks to ##
* [Angelo Compagnucci] (https://github.com/angeloc)
* [IDEA Soc. Coop.] (http://www.idea-on-line.it)
