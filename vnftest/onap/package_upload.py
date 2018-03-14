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

import copy
import logging
import time

import os
import yaml

from vnftest.common import constants as consts
from vnftest.common import rest_client
from vnftest.common.exceptions import MandatoryKeyException, InputParameterMissing
from vnftest.contexts.base import Context
from vnftest.crawlers.base import Crawler
from vnftest.onap.common.vnf_type_crawler import VnfTypeCrawler
from vnftest.onap.onap_api_call import OnapApiCall

LOG = logging.getLogger(__name__)


class PackageUpload(OnapApiCall):

    __step_type__ = "PackageUpload"

    def __init__(self, step_cfg, context_cfg, input_params):
        super(PackageUpload, self).__init__(step_cfg, context_cfg, input_params)

    def setup(self):
        super(PackageUpload, self).setup()
        self.input_cfg.append({'parameter_name': "package_file_path", 'value': Context.vnf_descriptor["csar_package_location"]})
