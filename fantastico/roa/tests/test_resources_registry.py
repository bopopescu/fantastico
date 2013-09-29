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
.. py:module:: fantastico.roa.tests.test_resources_registry
'''
from fantastico.roa.resource_decorator import Resource
from fantastico.roa.resources_registry import ResourcesRegistry
from fantastico.roa.roa_exceptions import FantasticoRoaDuplicateError
from fantastico.tests.base_case import FantasticoUnitTestsCase

class ResourcesRegistryTests(FantasticoUnitTestsCase):
    '''This class provides the test cases for resources registry.'''

    def cleanup(self):
        '''This method cleanup all affected dependencies after each test case.'''

        ResourcesRegistry.AVAILABLE_RESOURCES.clear()
        ResourcesRegistry.AVAILABLE_URL_RESOURCES.clear()

    def _register_resource_duplicate(self, resource1, resource2):
        '''This method executes register resource test case for duplicate exception.'''

        registry = ResourcesRegistry()

        registry.register_resource(resource1)

        with self.assertRaises(FantasticoRoaDuplicateError):
            registry.register_resource(resource2)

    def test_register_resource_duplicate_nameversion(self):
        '''This test case ensures an exception is raised when we try to register multiple resources with the same name and
        version.'''

        resource = Resource(name="app-setting", url="/app-settings")

        self._register_resource_duplicate(resource, resource)

    def test_register_resource_duplicate_url(self):
        '''This test case ensures different resources can not be registered under the same name.'''

        resource1 = Resource(name="app-setting", url="/app-settings")
        resource2 = Resource(name="custom-setting", url="/app-settings")

        self._register_resource_duplicate(resource1, resource2)

    def test_find_resource_by_name_notfound(self):
        '''This test case ensures no exception is raised when we try to retrieve a resource which is not registered.'''

        registry = ResourcesRegistry()

        resource = registry.find_by_name("app-setting", 1.0)

        self.assertIsNone(resource)

    def test_find_resource_by_name_version_notfound(self):
        '''This test case ensures no exception is raised when we try to retrieve a resource which does not have the version
        requested registered.'''

        registry = ResourcesRegistry()

        registry.register_resource(Resource(name="app-setting", url="/app-settings"))

        resource = registry.find_by_name("app-setting", 2.0)

        self.assertIsNone(resource)

    def _find_resource_by_name(self, name, version):
        '''This method provides a test case template for find by name method.'''

        resource = Resource(name=name, url="/%ss" % name)

        registry = ResourcesRegistry()

        registry.register_resource(resource)

        if version != "latest":
            found_resource = registry.find_by_name(name, version)
        else:
            found_resource = registry.find_by_name(name)

        self.assertEqual(resource.name, found_resource.name)
        self.assertEqual(resource.version, found_resource.version)
        self.assertEqual(resource.url, found_resource.url)
        self.assertEqual(resource.model, found_resource.model)

    def test_find_resource_by_name(self):
        '''This test case ensures registered resources can be return by name and version.'''

        self._find_resource_by_name("app-setting", 1.0)

    def test_find_resource_by_name_latest(self):
        '''This test case ensures latest versions of resources can be retrieved by resource name.'''

        self._find_resource_by_name("app-setting", "latest")

    def _find_resource_by_url(self, url, version):
        '''This method provides a test case template for find by url method.'''

        resource = Resource(name=url[1:-1], url=url)

        registry = ResourcesRegistry()

        registry.register_resource(resource)

        if version != "latest":
            found_resource = registry.find_by_url(url, version)
        else:
            found_resource = registry.find_by_url(url)

        self.assertEqual(resource.name, found_resource.name)
        self.assertEqual(resource.version, found_resource.version)
        self.assertEqual(resource.url, found_resource.url)
        self.assertEqual(resource.model, found_resource.model)

    def test_find_resource_by_url_notofound(self):
        '''This test case ensures None is returned if the resource can not be found by url.'''

        registry = ResourcesRegistry()

        resource = registry.find_by_url("/app-settings", "latest")

        self.assertIsNone(resource)

    def test_find_resource_by_url_version_notfound(self):
        '''This test case ensures None is returned if the resource url is found but the requested version is not registered.'''

        registry = ResourcesRegistry()

        registry.register_resource(Resource(name="app-setting", url="/app-settings", version="1.0"))

        resource = registry.find_by_url("/app-settings", 2.0)

        self.assertIsNone(resource)

    def test_find_resource_by_url(self):
        '''This test case ensures a resource can be found by url and version.'''

        self._find_resource_by_url("/app-settings", 1.0)

    def test_find_resource_by_url_latest(self):
        '''This test case ensures a resource can be found by url and latest version.'''

        self._find_resource_by_url("/app-settings", "latest")

    def test_all_resources_list(self):
        '''This test case ensures registered resources can be listed correctly (sorted by name).'''

        resource1 = Resource(name="triplex", url="/triplex", version=2.0)
        resource2 = Resource(name="triplex", url="/triplex", version=1.0)

        resource3 = Resource(name="abc", url="/abc", version=1.0)

        registry = ResourcesRegistry()

        registry.register_resource(resource1)
        registry.register_resource(resource2)
        registry.register_resource(resource3)

        expected_resources = [resource3, resource3, resource2, resource1, resource1]
        resources = registry.all_resources()

        self.assertEqual(resources, expected_resources)
