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

from vnftest.common.exceptions import MandatoryKeyException

from vnftest.crawlers import base
import logging

LOG = logging.getLogger(__name__)


class DefaultCrawler(base.Crawler):
    __crawler_type__ = 'default'

    def crawl(self, dictionary, path):
        if path.find("[") < 0:
            return path # the path is a hardcoded value

        path_list = path.split("[")
        value = dictionary
        for path_element in path_list:
            if path_element == "":
                continue
            path_element = path_element.replace("]", "")
            if isinstance(value, list):
                path_element = int(path_element)
            value = value[path_element]
        if value is None:
            raise MandatoryKeyException(key_name='param_path', class_name=str(dictionary))
        return value
