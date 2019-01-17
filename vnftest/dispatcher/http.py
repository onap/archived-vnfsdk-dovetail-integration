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
# yardstick/dispatcher/http.py

from __future__ import absolute_import

import logging
import os
from datetime import datetime

from oslo_serialization import jsonutils
import requests

from vnftest.dispatcher.base import Base as DispatchBase

LOG = logging.getLogger(__name__)


class HttpDispatcher(DispatchBase):
    """Dispatcher class for posting data into a http target.
    """

    __dispatcher_type__ = "Http"

    def __init__(self, conf):
        super(HttpDispatcher, self).__init__(conf)
        http_conf = conf['dispatcher_http']
        self.headers = {'Content-type': 'application/json'}
        self.timeout = int(http_conf.get('timeout', 5))
        self.target = http_conf.get('target', 'http://127.0.0.1:8000/results')

    def flush_result_data(self, id, data):
        if self.target == '':
            # if the target was not set, do not do anything
            LOG.error('Dispatcher target was not set, no data will'
                      'be posted.')
            return

        result = data['result']
        self.info = result['info']
        self.task_id = result['task_id']
        self.criteria = result['criteria']
        testcases = result['testcases']

        for testcase in testcases:
            self._upload_case_result(testcase)

    def _upload_case_result(self, testcase):
        try:
            step_data = testcase.get('steps', [])[0]
            step_result = step_data['results'][0]
        except IndexError:
            current_time = datetime.now()
        else:
            timestamp = float(step_result.get('timestamp', 0.0))
            current_time = datetime.fromtimestamp(timestamp)

        result = {
            "project_name": "vnftest",
            "case_name": testcase['name'],
            "description": "vnftest ci step status",
            "build_tag": os.environ.get('BUILD_TAG'),
            "criteria": testcase.get('criteria'),
            "start_date": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "stop_date": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "trust_indicator": "",
            "details": ""
        }

        try:
            LOG.debug('Test result : %s', result)
            res = requests.post(self.target,
                                data=jsonutils.dump_as_bytes(result),
                                headers=self.headers,
                                timeout=self.timeout)
            LOG.debug('Test result posting finished with status code'
                      ' %d.' % res.status_code)
        except Exception as err:
            LOG.exception('Failed to record result data: %s', err)
