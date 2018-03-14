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

from vnftest.common import utils

log = logging.getLogger(__name__)


class Crawler(object):

    @staticmethod
    def get_cls(crawler_type):
        """return class of specified type"""
        for crawler in utils.itersubclasses(Crawler):
            if crawler_type == crawler.__crawler_type__:
                return crawler
        raise RuntimeError("No such crawler_type %s" % crawler_type)

    def __init__(self):
        pass

    def crawl(self, dictionary, path):
        raise NotImplementedError
