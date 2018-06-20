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

from vnftest.crawlers.base import Crawler

from vnftest.common import openstack_utils, utils

import logging

from vnftest.steps import base

LOG = logging.getLogger(__name__)


class Heat(base.Step):
    __step_type__ = "Heat"

    def __init__(self, step_cfg, context, input_params):
        self.step_cfg = step_cfg
        self.context = context
        self.input_params = input_params
        self.output_cfg = None
        self.operation = None
        self.heat_stack_id = None

    def setup(self):
        options = self.step_cfg['options']
        self.operation = options.get("operation")
        self.output_cfg = options.get("output", {})
        heat_stack_id_def = options.get("heat_stack_id")
        self.heat_stack_id = utils.format(heat_stack_id_def, self.input_params)

    def run(self, result):
        op_result = getattr(self, self.operation)()
        op_result = utils.normalize_data_struct(op_result)
        output = Crawler.crawl(op_result, self.output_cfg)
        result.update(output)
        return output

    def get_stack_vms(self):
        return openstack_utils.get_stack_vms(self.heat_stack_id)
