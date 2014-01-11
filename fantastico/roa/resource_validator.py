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
.. py:module:: fantastico.roa.resource_validator
'''
from fantastico.utils.dictionary_object import DictionaryObject

class ResourceValidator(object):
    '''This class provides the base for all validators which can be used for resources.

    .. code-block:: python

        class AppSettingValidator(ResourceValidator):
            def validate(self, resource, request):
                errors = []

                if resource.name == "unsupported":
                    errors.append("Invalid setting name: %s" % resource.name)

                if len(resource.value) == 0:
                    errors.append("Setting %s value can not be empty. %s" % resource.name)

                if len(errors) == 0:
                    return

                raise FantasticoRoaError(errors)

            def format_collection(self, resources, request):
                # we can safely retrieve the full collection of resources so nothing has to be done here.

            def format_resource(self, resource, request):
                # we can safely retrieve the resource so nothing has to be done here.

    Every method from validator receives the current http request in order to give access to resource validators to security
    context and other contexts which might be necessary.
    '''

    def validate(self, resource, request): # pylint: disable=W0613
        '''This method must be overriden by each subclass in order to provide the validation logic required for the given
        resource. The resource received as an argument represents an instance of the model used to describe the resource.
        This method can raise unexpected exceptions. It is recommended to use
        :py:class:`fantastico.roa.roa_exceptions.FantasticoRoaError`.'''

        if not resource:
            return False

        return True

    def format_collection(self, resources, request): # pylint: disable=W0613
        '''This method must be overriden by each subclass in order to provide custom logic which must be executed after
        a collection is fetched from database. By default, this method simply iterates over the list of available resources and
        invoke format_resource.

        Usually you will want to override this method in order to suppress sensitive data to be sent to clients.'''

        resources = resources or []

        for resource in resources:
            self.format_resource(DictionaryObject(resource, immutable=False), request)

    def format_resource(self, resource, request): # pylint: disable=W0613
        '''This method must be overriden by each subclass in order to provide custom logic which must be executed after a resource
        is fetched.

        Usually you will want to override this method in order to suppress sensitive data to be sent to clients.'''

        pass
