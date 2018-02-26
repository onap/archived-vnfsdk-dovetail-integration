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
# yardstick/common/httpClient.py

from __future__ import absolute_import

import logging
import time

from oslo_serialization import jsonutils
import requests

logger = logging.getLogger(__name__)


class HttpClient(object):

    def post(self, url, data, timeout=0):
        data = jsonutils.dump_as_bytes(data)
        headers = {'Content-Type': 'application/json'}
        t_end = time.time() + timeout
        while True:
            try:
                response = requests.post(url, data=data, headers=headers)
                result = response.json()
                logger.debug('The result is: %s', result)
                return result
            except Exception:
                if time.time() > t_end:
                    logger.exception('')
                    raise
            time.sleep(1)

    def get(self, url):
        response = requests.get(url)
        return response.json()
