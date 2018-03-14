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


class VnfTypeCrawler(DefaultCrawler):
    __crawler_type__ = 'VnfTypeCrawler'

    def crawl(self, dictionary, path):
        index = 0
        vnf_type = dictionary['groups'][0]['name']
        if ".." not in vnf_type:
            index = 1
        dictionary = dictionary['groups'][index]
        return super(VnfTypeCrawler, self).crawl(dictionary, path)
