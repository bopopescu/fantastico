'''
Copyright 2013 Cosnita Radu Viorel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. codeauthor:: Radu Viorel Cosnita <radu.cosnita@gmail.com>
.. py:module:: fantastico.sdk.sdk_decorators
'''
from fantastico.sdk.sdk_core import SdkCommandsRegistry

class SdkCommand(object):
    '''This decorator describe the sdk commands metadata:

    #. name
    #. target (which is the main purpose of the command. E.g: fantastico - this mean command is designed to work as a subcommand for fantastico cmd).

    It is used in conjunction with :py:class:`fantastico.sdk.sdk_core.SdkCommand`. Each sdk command decorated with this
    decorator automatically receives **get_name** and **get_target** methods.'''

    def __init__(self, name, help, target=None):
        self._name = name
        self._target = target
        self._help = help

    def __call__(self, cls):
        '''This method simply adds get_name method to the command class.'''

        cls.get_name = lambda ctx = None: self._name
        cls.get_help = lambda ctx = None: self._help
        cls.get_target = lambda ctx = None: self._target

        SdkCommandsRegistry.add_command(self._name, cls)

        return cls
