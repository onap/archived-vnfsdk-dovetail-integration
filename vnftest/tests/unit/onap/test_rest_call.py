##############################################################################
# Copyright 2018 EuropeanSoftwareMarketingLtd.
# ===================================================================
#  Licensed under the ApacheLicense, Version2.0 (the"License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License
##############################################################################

import mock
import testtools
from vnftest.contexts.base import Context
from vnftest.core import task


class RestCallTestCase(testtools.TestCase):

    step = {
      'name': 'DummyName',
      'type': 'RestCall',
      'options': {
        'file': "dummy.yaml",
        'input':
        [{
          'parameter_name': "input1",
          'value': "value1"
        }],
        'output':
        [{
          'parameter_name': "output1",
          'value': "[value]"
        }]},
      'sla': {
        'action': 'assert',
        'value': "{output1}",
        'equals': "output1",
        'retries': 5,
        'interval': 5}
    }
    NAME = 'sample'

    def setUp(self):
        super(RestCallTestCase, self).setUp()

    @mock.patch('vnftest.steps.rest_call.RestCall.execute_operation_impl')
    def test_run(self, mock_execute_operation):
        mock_execute_operation.return_value = {'body': {'value': 'output1'}}
        t = task.Task({})
        context_cfg = {}
        context = Context.get("CSAR")
        context.init(context_cfg)
        t.context = context
        output = t._run([RestCallTestCase.step], 'dummy_case', False, "vnftest.out", {})
        self.assertEquals(output[0]['data']['output1'], 'output1')
