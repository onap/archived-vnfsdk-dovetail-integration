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
# yardstick/cmd/commands/step.py
""" Handler for vnftest command 'step' """

from __future__ import print_function
from __future__ import absolute_import
from vnftest.onap.core.step import Steps
from vnftest.common.utils import cliargs
from vnftest.cmd.commands import change_osloobj_to_paras


class StepCommands(object):     # pragma: no cover
    """Step commands.

       Set of commands to discover and display step types.
    """

    def do_list(self, args):
        """List existing step types"""
        param = change_osloobj_to_paras(args)
        Steps().list_all(param)

    @cliargs("type", type=str, help="runner type", nargs=1)
    def do_show(self, args):
        """Show details of a specific step type"""
        param = change_osloobj_to_paras(args)
        Steps().show(param)
