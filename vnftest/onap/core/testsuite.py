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
# yardstick/benchmark/core/testsuite.py

""" Handler for vnftest command 'testcase' """
from __future__ import absolute_import
from __future__ import print_function

import os
import logging

from vnftest.common import constants as consts

LOG = logging.getLogger(__name__)


class Testsuite(object):
    """Testcase commands.

       Set of commands to discover and display test cases.
    """

    def list_all(self, args):
        """List existing test cases"""

        testsuite_list = self._get_testsuite_file_list()

        return testsuite_list

    def _get_testsuite_file_list(self):
        try:
            testsuite_files = sorted(os.listdir(consts.TESTSUITE_DIR))
        except OSError:
            LOG.exception('Failed to list dir:\n%s\n', consts.TESTSUITE_DIR)
            raise

        return testsuite_files
