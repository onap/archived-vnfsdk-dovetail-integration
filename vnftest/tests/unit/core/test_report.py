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
# vnftest comment: this is a modified copy of
# yardstick/tests/unit/benchmark/core/test_report.py

from __future__ import print_function

from __future__ import absolute_import

import unittest
import uuid

try:
    from unittest import mock
except ImportError:
    import mock

from vnftest.core import report
from vnftest.cmd.commands import change_osloobj_to_paras

FAKE_YAML_NAME = 'fake_name'
FAKE_TASK_ID = str(uuid.uuid4())
DUMMY_TASK_ID = 'aaaaaa-aaaaaaaa-aaaaaaaaaa-aaaaaa'


class ReportTestCase(unittest.TestCase):

    def setUp(self):
        super(ReportTestCase, self).setUp()
        self.param = change_osloobj_to_paras({})
        self.param.yaml_name = [FAKE_YAML_NAME]
        self.param.task_id = [FAKE_TASK_ID]
        self.rep = report.Report()

    @mock.patch('vnftest.core.report.Report._validate')
    def test_generate_success(self, mock_valid):
        self.rep.generate(self.param)
        mock_valid.assert_called_once_with(FAKE_YAML_NAME, FAKE_TASK_ID)

    # pylint: disable=deprecated-method
    def test_invalid_yaml_name(self):
        self.assertRaisesRegexp(ValueError, "yaml*", self.rep._validate,
                                'F@KE_NAME', FAKE_TASK_ID)

    # pylint: disable=deprecated-method
    def test_invalid_task_id(self):
        self.assertRaisesRegexp(ValueError, "task*", self.rep._validate,
                                FAKE_YAML_NAME, DUMMY_TASK_ID)
