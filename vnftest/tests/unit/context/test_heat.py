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

import unittest

import mock
import os

from vnftest.contexts.heat import HeatContext

from vnftest.common import constants as consts
from vnftest.core import task
from vnftest.common import openstack_utils


class HeatTestCase(unittest.TestCase):

    @mock.patch.object(HeatContext, 'check_environment')
    @mock.patch.object(HeatContext, '_create_new_stack')
    @mock.patch.object(HeatContext, 'get_neutron_info')
    @mock.patch.object(openstack_utils, 'get_shade_client')
    @mock.patch.object(openstack_utils, 'get_shade_operator_client')
    def test_heat(self, mock_check_env, mock_create, mocke_neutron, shade_client, operator_client):
        params = {
            "task_id": "123",
            "name": "heat-test",
            "image": "test_image",
            "flavor" : "test_flavor",
            "user": "test_user",
            "servers": {}}
        mock_create.return_value = {}
        h = HeatContext()
        h.init(params)
        h.deploy()
        h._get_server("dummy")
        h.undeploy()
