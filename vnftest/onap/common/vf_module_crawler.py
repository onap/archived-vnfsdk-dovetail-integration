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
from vnftest.crawlers.default import DefaultCrawler
import logging

LOG = logging.getLogger(__name__)


class VfModuleCrawler(DefaultCrawler):
    __crawler_type__ = 'VfModuleCrawler'

    def crawl(self, dictionary, path):
        result = {}
        for componentInstance in dictionary['componentInstances']:
            for groupInstance in componentInstance['groupInstances']:
                # get the module name without additions. Example:
                # original name: TestVsp2007..policyVNF_infinity..module-5
                # name without additions: policyVNF_infinity
                module_name = groupInstance['groupName'].split("..")
                module_name = str(module_name[1])
                result[module_name] = groupInstance
        return result
