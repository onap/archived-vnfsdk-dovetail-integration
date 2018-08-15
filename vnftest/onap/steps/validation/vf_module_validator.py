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

from __future__ import absolute_import

import logging

from vnftest.steps.rest_call import RestCall

from vnftest.common import openstack_utils, utils
from vnftest.steps import base

LOG = logging.getLogger(__name__)


class VfModuleValidator(base.Step):
    __step_type__ = "VfModuleValidator"

    def __init__(self, step_cfg, context, input_params):
        self.validation_cfg = step_cfg
        self.context = context
        self.input_params = input_params
        self.vnf_instance_id = None
        self.vf_module_instance_id = None

    def setup(self):
        options = self.validation_cfg['options']
        vnf_instance_id_def = options.get("vnf_instance_id")
        self.vnf_instance_id = utils.format(vnf_instance_id_def, self.input_params)
        vf_module_instance_id_def = options.get("vf_module_instance_id")
        self.vf_module_instance_id = utils.format(vf_module_instance_id_def, self.input_params)

    def run(self, result):
        heat_stack_id = self.get_heat_stack_id()
        vm_resources = openstack_utils.get_stack_vms(heat_stack_id)
        for resource in vm_resources:
            assert resource.resource_status == 'CREATE_COMPLETE', "Unexpected VM status: " + str(resource.resource_status)

    # Get the heat stack id from AAI
    def get_heat_stack_id(self):
        step_conf = {}
        step_conf['file'] = "aai_get_vf_module.yaml"
        step_conf['input'] = [{'parameter_name': 'vnf_instance_id',
                               'value': self.vnf_instance_id},
                              {'parameter_name': 'vf_module_instance_id',
                               'value': self.vf_module_instance_id}
                              ]
        step_conf['output'] = {'heat_stack_id': '[heat-stack-id]'}
        options = {'options': step_conf}
        rest_call = RestCall(options, self.context, self.input_params)
        output = rest_call.run({})
        return output['heat_stack_id']

