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
# yardstick/benchmark/core/testcase.py

""" Handler for vnftest command 'testcase' """
from __future__ import absolute_import
from __future__ import print_function

import os
import logging

from vnftest.common.task_template import TaskTemplate
from vnftest.common import constants as consts
from vnftest.common.yaml_loader import yaml_load

LOG = logging.getLogger(__name__)


class Testcase(object):
    """Testcase commands.

       Set of commands to discover and display test cases.
    """

    def list_all(self, args):
        """List existing test cases"""

        testcase_files = self._get_testcase_file_list()
        testcase_list = [self._get_record(f) for f in testcase_files]

        return testcase_list

    def _get_testcase_file_list(self):
        try:
            testcase_files = sorted(os.listdir(consts.TESTCASE_DIR))
        except OSError:
            LOG.exception('Failed to list dir:\n%s\n', consts.TESTCASE_DIR)
            raise

        return testcase_files

    def _get_record(self, testcase_file):

        file_path = os.path.join(consts.TESTCASE_DIR, testcase_file)
        with open(file_path) as f:
            try:
                testcase_info = f.read()
            except IOError:
                LOG.exception('Failed to load test case:\n%s\n', testcase_file)
                raise

        description, installer, deploy_steps = self._parse_testcase(
            testcase_info)

        record = {
            'Name': testcase_file.split(".")[0],
            'Description': description,
            'installer': installer,
            'deploy_steps': deploy_steps
        }

        return record

    def _parse_testcase(self, testcase_info):
        kw = {}
        kw['vnf_descriptor'] = {}
        rendered_testcase = TaskTemplate.render(testcase_info, **kw)
        testcase_cfg = yaml_load(rendered_testcase)

        test_precondition = testcase_cfg.get('precondition', {})
        installer_type = test_precondition.get('installer_type', 'all')
        deploy_steps = test_precondition.get('deploy_steps', 'all')

        description = self._get_description(testcase_cfg)

        return description, installer_type, deploy_steps

    def _get_description(self, testcase_cfg):
        try:
            description_list = testcase_cfg['description'].split(';')
        except KeyError:
            return ''
        else:
            try:
                return description_list[1].replace(os.linesep, '').strip()
            except IndexError:
                return description_list[0].replace(os.linesep, '').strip()

    def show(self, args):
        """Show details of a specific test case"""
        testcase_name = args.casename[0]
        testcase_path = os.path.join(consts.TESTCASE_DIR,
                                     testcase_name + ".yaml")
        with open(testcase_path) as f:
            try:
                testcase_info = f.read()
            except IOError:
                LOG.exception('Failed to load test case:\n%s\n', testcase_path)
                raise

            print(testcase_info)
        return True
