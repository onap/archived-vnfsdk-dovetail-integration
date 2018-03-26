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
# yardstick/tests/unit/common/test_httpClient.py

from __future__ import absolute_import

import unittest

import mock
from oslo_serialization import jsonutils

from vnftest.common import httpClient


class HttpClientTestCase(unittest.TestCase):

    @mock.patch('vnftest.common.httpClient.requests')
    def test_post(self, mock_requests):
        url = 'http://localhost:5000/hello'
        data = {'hello': 'world'}
        headers = {'Content-Type': 'application/json'}
        httpClient.HttpClient().post(url, data)
        mock_requests.post.assert_called_with(
            url, data=jsonutils.dump_as_bytes(data),
            headers=headers)

    @mock.patch('vnftest.common.httpClient.requests')
    def test_get(self, mock_requests):
        url = 'http://localhost:5000/hello'
        httpClient.HttpClient().get(url)
        mock_requests.get.assert_called_with(url)
