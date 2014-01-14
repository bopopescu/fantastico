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
.. py:module:: fantastico.contrib.oauth2_idp.models.tests.itest_persons_api
'''
from fantastico.settings import SettingsFacade
import http
import json
from fantastico.server.tests.itest_dev_server import DevServerIntegration

class PersonResourceIntegrationTests(DevServerIntegration):
    '''This class provides the integration tests required for person resource.'''

    _access_token = None

    def init(self):
        '''This method is invoked automatically before each test case.'''

        oauth2_idp = SettingsFacade().get("oauth2_idp")
        self._access_token = self._get_oauth2_token(client_id=oauth2_idp["client_id"], user_id=1,
                                                    scopes="user.profile.update user.profile.delete user.profile.read")

    def test_create_person_unauthorized(self):
        '''This test case ensures a person can not be created through persons api.'''

        person = {"first_name": "John"}

        self._invoke_persons_template_unauthorized("POST", person)

    def test_read_persons_unauthorized(self):
        '''This test case ensures persons can not be retrieved through api.'''

        self._invoke_persons_template_unauthorized("GET")

    def _invoke_persons_template_unauthorized(self, method, person=None, person_id=None):
        '''This method provides a template for invoking persons api and asserting for unauthorized response.'''

        endpoint = "/api/latest/oauth-idp-person"

        if person_id:
            endpoint = "%s/%s" % (endpoint, person_id)

        results = {}

        if person:
            person = json.dumps(person)

        def create_person(server):
            '''This method tries to create a person through api.'''

            http_conn = http.client.HTTPConnection(host=server.hostname, port=server.port)

            http_conn.request(method, endpoint, body=person)

            results["response"] = http_conn.getresponse()

            http_conn.close()

        def assert_unauthorized(server):
            '''This method is inoked for asserting unauthorized response code was returned.'''

            response = results.get("response")

            self.assertIsNotNone(response)
            self.assertEqual(401, response.status)

        self._run_test_against_dev_server(create_person, assert_unauthorized)
