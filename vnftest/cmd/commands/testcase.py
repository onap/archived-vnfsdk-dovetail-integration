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
# yardstick/cmd/commands/testcase.py
""" Handler for vnftest command 'testcase' """
from __future__ import absolute_import

import prettytable

from vnftest.onap.core.testcase import Testcase
from vnftest.common.utils import cliargs
from vnftest.cmd.commands import change_osloobj_to_paras
from vnftest.cmd.commands import Commands


class TestcaseCommands(Commands):
    """Testcase commands.

       Set of commands to discover and display test cases.
    """

    def do_list(self, *args):
        testcase_list = ""
        self._format_print(testcase_list)

    @cliargs("casename", type=str, help="test case name", nargs=1)
    def do_show(self, args):
        """Show details of a specific test case"""
        param = change_osloobj_to_paras(args)
        Testcase().show(param)

    def _format_print(self, testcase_list):
        """format output"""
        case_table = prettytable.PrettyTable(['Testcase Name', 'Description'])
        case_table.align = 'l'
        for testcase_record in testcase_list:
            case_table.add_row([testcase_record['Name'], testcase_record['Description']])
        print(case_table)
